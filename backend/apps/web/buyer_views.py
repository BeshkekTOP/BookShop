"""Views для покупателей - отзывы, заказы"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from backend.apps.core.decorators import buyer_required
from backend.apps.catalog.models import Book
from backend.apps.reviews.models import Review


@buyer_required
@require_http_methods(["GET", "POST"])
def add_review(request, book_id):
    """Добавить или редактировать отзыв на книгу"""
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        text = request.POST.get('text', '').strip()
        
        if rating < 1 or rating > 5:
            messages.error(request, "Рейтинг должен быть от 1 до 5")
            return redirect(f'/books/{book_id}/')
        
        # Проверяем, существует ли уже отзыв
        review, created = Review.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'rating': rating, 'text': text}
        )
        
        if not created:
            review.rating = rating
            review.text = text
            review.save()
            messages.success(request, "Отзыв обновлён")
        else:
            messages.success(request, "Отзыв добавлен")
        
        return redirect(f'/books/{book_id}/')
    
    # GET - показываем форму
    # Проверяем, есть ли уже отзыв
    existing_review = Review.objects.filter(user=request.user, book=book).first()
    
    return render(request, 'web/buyer/add_review.html', {
        'book': book,
        'existing_review': existing_review
    })


@buyer_required
@require_http_methods(["POST"])
def delete_review(request, book_id):
    """Удалить отзыв на книгу"""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        review = Review.objects.get(user=request.user, book=book)
        review.delete()
        messages.success(request, "Отзыв удалён")
    except Review.DoesNotExist:
        messages.error(request, "Отзыв не найден")
    
    return redirect(f'/books/{book_id}/')


@buyer_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """Редактирование профиля покупателя"""
    from backend.apps.users.models import Profile
    from django import forms
    
    class ProfileForm(forms.ModelForm):
        class Meta:
            model = Profile
            fields = ["phone", "address", "city"]
    
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'web/buyer/edit_profile.html', {"form": form})


@buyer_required
@require_http_methods(["GET", "POST"])
def checkout_detailed(request):
    """Детальная страница оформления заказа"""
    from backend.apps.orders.models import Cart
    from backend.apps.catalog.models import Inventory
    from backend.apps.users.models import Profile
    from decimal import Decimal
    
    cart = Cart.objects.filter(user=request.user).prefetch_related("items__book").first()
    
    if not cart or cart.items.count() == 0:
        messages.error(request, "Корзина пуста")
        return redirect('cart')
    
    # Получаем профиль пользователя
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Проверка наличия
        for item in cart.items.select_related('book').all():
            inventory, _ = Inventory.objects.get_or_create(book=item.book)
            if inventory.available < item.quantity:
                messages.error(request, f"Недостаточно на складе: {item.book.title}")
                return redirect('cart')
        
        # Создание заказа
        from backend.apps.orders.models import Order, OrderItem
        
        order = Order.objects.create(
            user=request.user,
            status="processing",
            total_amount=Decimal("0"),
            shipping_address=request.POST.get('address', profile.address or ''),
            shipping_city=request.POST.get('city', profile.city or ''),
            notes=request.POST.get('notes', '')
        )
        
        total = Decimal("0")
        for item in cart.items.select_related('book').all():
            price = item.book.price
            OrderItem.objects.create(order=order, book=item.book, price=price, quantity=item.quantity)
            total += price * item.quantity
            inventory, _ = Inventory.objects.get_or_create(book=item.book)
            inventory.stock = max(0, inventory.stock - item.quantity)
            inventory.save()
        
        order.total_amount = total
        order.save()
        
        # Очистка корзины
        cart.items.all().delete()
        return redirect('checkout-success', order_id=order.id)
    
    # GET - показываем форму
    items = cart.items.select_related('book').all()
    total = sum((it.book.price * it.quantity for it in items), start=Decimal('0'))
    
    return render(request, 'web/buyer/checkout_detailed.html', {
        'cart': cart,
        'items': items,
        'total': total,
        'profile': profile
    })


@buyer_required
def orders_history(request):
    """История заказов покупателя"""
    from backend.apps.orders.models import Order
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:20]
    return render(request, 'web/buyer/orders_history.html', {'orders': orders})


@buyer_required
def order_detail(request, order_id):
    """Детали заказа покупателя"""
    from backend.apps.orders.models import Order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'web/buyer/order_detail.html', {'order': order})
