from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.db.models import Q, Avg, Count
from django.views.decorators.http import require_http_methods

from backend.apps.catalog.models import Book, Category, Author, Inventory, BookAuthors
from backend.apps.orders.models import Cart, CartItem, Order, OrderItem
from backend.apps.users.models import Profile
from backend.apps.core.decorators import guest_required, buyer_required, admin_required
from django import forms
from decimal import Decimal, InvalidOperation

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации с дополнительными полями: email, first_name, last_name"""
    email = forms.EmailField(
        required=True,
        label='Email',
        help_text='Введите ваш email адрес'
    )
    first_name = forms.CharField(
        required=True,
        max_length=150,
        label='Имя',
        help_text='Введите ваше имя'
    )
    last_name = forms.CharField(
        required=True,
        max_length=150,
        label='Фамилия',
        help_text='Введите вашу фамилию'
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["phone", "address"]


class BookForm(forms.ModelForm):
    author_ids = forms.ModelMultipleChoiceField(queryset=Author.objects.all(), required=False)

    class Meta:
        model = Book
        fields = ["title", "isbn", "description", "category", "price"]


def home(request):
    latest_books = Book.objects.order_by('-created_at')[:8]
    return render(request, 'web/home.html', {"latest_books": latest_books})


def catalog_list(request):
    q = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    rating_min = request.GET.get('rating_min', '')
    
    qs = Book.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    
    # Поиск по названию, ISBN
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(isbn__icontains=q) | 
                       Q(book_authors__author__first_name__icontains=q) |
                       Q(book_authors__author__last_name__icontains=q))
    
    # Фильтрация по категории
    if category_filter:
        qs = qs.filter(category__slug=category_filter)
    
    # Фильтрация по цене
    if price_min:
        try:
            qs = qs.filter(price__gte=Decimal(price_min))
        except (ValueError, InvalidOperation):
            pass
    if price_max:
        try:
            qs = qs.filter(price__lte=Decimal(price_max))
        except (ValueError, InvalidOperation):
            pass
    
    # Фильтрация по рейтингу
    if rating_min:
        try:
            qs = qs.filter(rating__gte=Decimal(rating_min))
        except (ValueError, InvalidOperation):
            pass
    
    # Исключаем дубликаты
    qs = qs.distinct()
    
    # Список категорий для фильтра
    categories = Category.objects.all()
    
    return render(request, 'web/catalog.html', {
        "books": qs,
        "categories": categories,
        "q": q
    })


def book_detail(request, pk: int):
    """Детальная информация о книге - доступна всем (включая гостей)"""
    book = get_object_or_404(Book, pk=pk)
    
    # Получаем авторов книги
    authors = book.book_authors.select_related('author').all()
    
    # Получаем информацию о наличии на складе
    try:
        inventory = book.inventory
    except Inventory.DoesNotExist:
        inventory = None
    
    # Получаем отзывы (только для просмотра)
    reviews = book.reviews.select_related('user').all()[:10]  # Последние 10 отзывов
    
    return render(request, 'web/book_detail.html', {
        "book": book,
        "authors": [a.author for a in authors],
        "inventory": inventory,
        "reviews": reviews
    })


@buyer_required
@require_http_methods(["GET", "POST"])
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if request.method == "POST":
        action = request.POST.get("action", "add")
        book_id = request.POST.get("book")
        qty = int(request.POST.get("quantity", "1") or 1)
        if action == "add" and book_id:
            # Проверка наличия товара на складе
            from backend.apps.catalog.models import Inventory, Book
            book = get_object_or_404(Book, id=book_id)
            inventory, _ = Inventory.objects.get_or_create(book=book)
            
            # Проверяем доступное количество
            available = inventory.available
            
            if available <= 0:
                messages.error(request, f"Товар '{book.title}' отсутствует на складе")
                return redirect('catalog')
            
            # Проверяем, не превышает ли запрашиваемое количество доступное
            existing_item = CartItem.objects.filter(cart=cart, book_id=book_id).first()
            current_qty = existing_item.quantity if existing_item else 0
            requested_qty = current_qty + qty
            
            if requested_qty > available:
                messages.error(request, f"Недостаточно товара на складе. Доступно: {available} шт.")
                return redirect('catalog')
            
            item, created = CartItem.objects.get_or_create(cart=cart, book_id=book_id, defaults={"quantity": qty})
            if not created:
                item.quantity = item.quantity + qty
                item.save()
            messages.success(request, "Товар добавлен в корзину")
        elif action in ("inc", "dec") and book_id:
            try:
                item = CartItem.objects.get(cart=cart, book_id=book_id)
                from backend.apps.catalog.models import Inventory
                inventory = Inventory.objects.get(book=item.book)
                available = inventory.available
                
                if action == "inc":
                    # Проверяем, не превышает ли увеличенное количество доступное
                    if item.quantity + 1 > available:
                        messages.error(request, f"Недостаточно товара на складе. Доступно: {available} шт.")
                    else:
                        item.quantity += 1
                        item.save()
                        messages.success(request, "Корзина обновлена")
                else:
                    if item.quantity > 1:
                        item.quantity -= 1
                        item.save()
                        messages.success(request, "Корзина обновлена")
                    else:
                        item.delete()
                        messages.success(request, "Товар удалён из корзины")
            except CartItem.DoesNotExist:
                pass
            except Inventory.DoesNotExist:
                messages.error(request, "Информация о товаре не найдена")
        elif action == "remove" and book_id:
            CartItem.objects.filter(cart=cart, book_id=book_id).delete()
            messages.success(request, "Товар удалён из корзины")
        return redirect('cart')

    items = cart.items.select_related('book').all()
    
    # Проверяем наличие товаров и показываем предупреждения
    for item in items:
        from backend.apps.catalog.models import Inventory
        try:
            inventory = Inventory.objects.get(book=item.book)
            if inventory.available < item.quantity:
                if inventory.available > 0:
                    messages.warning(request, f"Товар '{item.book.title}': доступно только {inventory.available} шт., в корзине {item.quantity} шт.")
                else:
                    messages.error(request, f"Товар '{item.book.title}' отсутствует на складе")
        except Inventory.DoesNotExist:
            messages.error(request, f"Информация о товаре '{item.book.title}' не найдена")
    
    total = sum((it.book.price * it.quantity for it in items), start=Decimal('0'))
    return render(request, 'web/cart.html', {"cart": cart, "items": items, "total": total})


@buyer_required
@transaction.atomic
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).prefetch_related("items__book").first()
    if not cart or cart.items.count() == 0:
        messages.error(request, "Корзина пуста")
        return redirect('cart')

    # Проверка наличия
    for item in cart.items.select_related('book').all():
        inv = Inventory.objects.select_for_update().get(book=item.book)
        if inv.stock - inv.reserved < item.quantity:
            messages.error(request, f"Недостаточно на складе: {item.book.title}")
            return redirect('cart')

    # Создание заказа
    order = Order.objects.create(user=request.user, status="processing", total_amount=Decimal('0'))
    total = Decimal('0')
    for item in cart.items.select_related('book').all():
        price = item.book.price
        OrderItem.objects.create(order=order, book=item.book, price=price, quantity=item.quantity)
        total += price * item.quantity
        inv = Inventory.objects.select_for_update().get(book=item.book)
        inv.stock = max(0, inv.stock - item.quantity)
        inv.save()

    order.total_amount = total
    order.save()
    # Очистка корзины
    cart.items.all().delete()
    return render(request, 'web/checkout_success.html', {"order": order})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Логируем вход в систему
            from backend.apps.core.models import AuditLog
            AuditLog.objects.create(
                action='login',
                actor=user,
                description=f'Пользователь {user.username} вошел в систему',
                method='POST',
                ip_address=request.META.get('REMOTE_ADDR'),
                path=request.path,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            return redirect('catalog')
    else:
        form = AuthenticationForm(request)
    return render(request, 'web/login.html', {"form": form})


@guest_required
def register_view(request):
    """Регистрация доступна только гостям"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль для нового пользователя
            Profile.objects.get_or_create(user=user)
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            if user:
                # Логируем регистрацию
                from backend.apps.core.models import AuditLog
                AuditLog.objects.create(
                    action='registered',
                    actor=user,
                    description=f'Пользователь {user.username} ({user.email}) зарегистрировался в системе',
                    method='POST',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    path=request.path,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                login(request, user)
                messages.success(request, 'Добро пожаловать! Регистрация прошла успешно.')
                return redirect('catalog')
    else:
        form = CustomUserCreationForm()
    return render(request, 'web/register.html', {"form": form})


@login_required
def logout_view(request):
    user = request.user
    # Логируем выход из системы
    from backend.apps.core.models import AuditLog
    AuditLog.objects.create(
        action='logout',
        actor=user,
        description=f'Пользователь {user.username} вышел из системы',
        method='GET',
        ip_address=request.META.get('REMOTE_ADDR'),
        path=request.path,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    logout(request)
    return redirect('login')


@buyer_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'web/profile.html', {"form": form})


def checkout_success(request, order_id):
    """Страница успешного оформления заказа"""
    from backend.apps.orders.models import Order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'web/checkout_success.html', {"order": order})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_books(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            auths = form.cleaned_data.get('author_ids')
            if auths is not None:
                from backend.apps.catalog.models import BookAuthors
                BookAuthors.objects.filter(book=book).delete()
                for a in auths:
                    BookAuthors.objects.create(book=book, author=a)
            messages.success(request, 'Книга добавлена')
            return redirect('admin-books')
    else:
        form = BookForm()
    books = Book.objects.select_related('category').all().order_by('title')
    return render(request, 'web/admin_books.html', {"form": form, "books": books})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_book_edit(request, pk: int):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            auths = form.cleaned_data.get('author_ids')
            if auths is not None:
                from backend.apps.catalog.models import BookAuthors
                BookAuthors.objects.filter(book=book).delete()
                for a in auths:
                    BookAuthors.objects.create(book=book, author=a)
            messages.success(request, 'Книга обновлена')
            return redirect('admin-books')
    else:
        form = BookForm(instance=book)
    return render(request, 'web/admin_book_edit.html', {"form": form, "book": book})


@admin_required
@require_http_methods(["POST"]) 
def admin_book_delete(request, pk: int):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, 'Книга удалена')
    return redirect('admin-books')


@admin_required
@require_http_methods(["GET", "POST"])
def admin_authors(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name','').strip()
        last_name = request.POST.get('last_name','').strip()
        if first_name and last_name:
            Author.objects.get_or_create(first_name=first_name, last_name=last_name)
            messages.success(request, 'Автор добавлен')
            return redirect('admin-authors')
    authors = Author.objects.all().order_by('last_name','first_name')
    return render(request, 'web/admin_authors.html', {"authors": authors})


@admin_required
@require_http_methods(["GET", "POST"])
def admin_categories(request):
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        slug = request.POST.get('slug','').strip()
        if name and slug:
            Category.objects.get_or_create(name=name, slug=slug)
            messages.success(request, 'Категория добавлена')
            return redirect('admin-categories')
    categories = Category.objects.all().order_by('name')
    return render(request, 'web/admin_categories.html', {"categories": categories})
