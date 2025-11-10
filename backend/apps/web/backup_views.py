"""Views для управления резервными копиями"""
import os
import subprocess
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from backend.apps.core.decorators import admin_required
from backend.apps.core.models import AuditLog
from datetime import datetime


@admin_required
def backup_list(request):
    """Список резервных копий"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    # Создаем директорию если её нет
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Получаем список файлов резервных копий
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith(('.sql', '.db')):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created_at': datetime.fromtimestamp(file_stat.st_mtime),
                    'path': filepath
                })
    
    # Сортируем по дате создания (новые сверху)
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render(request, 'web/admin/backups.html', {
        'backups': backups
    })


@admin_required
@require_http_methods(["POST"])
def backup_create(request):
    """Создание резервной копии"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    # Создаем директорию если её нет
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"bookstore_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Получаем настройки БД из settings
        db_settings = settings.DATABASES['default']
        db_name = db_settings.get('NAME', 'bookstore')
        db_user = db_settings.get('USER', 'bookstore')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        db_password = db_settings.get('PASSWORD', '')
        
        # Создаем резервную копию
        # Используем pg_dump через subprocess
        env = os.environ.copy()
        if db_password:
            env['PGPASSWORD'] = db_password
        
        # Проверяем, используется ли SQLite (для разработки)
        if 'sqlite' in db_settings.get('ENGINE', '').lower():
            # Для SQLite используем простой способ
            import shutil
            db_path = db_settings.get('NAME')
            if os.path.exists(db_path):
                backup_path_db = backup_path.replace('.sql', '.db')
                shutil.copy2(db_path, backup_path_db)
                backup_path = backup_path_db
                result_code = 0
            else:
                raise Exception('База данных SQLite не найдена')
        else:
            # Для PostgreSQL
            cmd = [
                'pg_dump',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', db_name,
                '-F', 'p',
                '-f', backup_path
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            result_code = result.returncode
        
        if result_code == 0:
            final_filename = os.path.basename(backup_path)
            # Логируем создание резервной копии
            AuditLog.objects.create(
                action='backup_created',
                actor=request.user,
                description=f'Администратор {request.user.username} создал резервную копию: {final_filename}',
                method='POST',
                ip_address=request.META.get('REMOTE_ADDR'),
                path=request.path,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                new_data={'filename': final_filename, 'size': os.path.getsize(backup_path)}
            )
            messages.success(request, f'Резервная копия успешно создана: {final_filename}')
        else:
            error_msg = result.stderr if 'result' in locals() else 'Ошибка создания резервной копии'
            messages.error(request, f'Ошибка при создании резервной копии: {error_msg}')
    
    except Exception as e:
        messages.error(request, f'Ошибка при создании резервной копии: {str(e)}')
    
    return redirect('admin-backups')


@admin_required
def backup_download(request, filename):
    """Скачивание резервной копии"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    if not os.path.exists(filepath) or not filename.endswith(('.sql', '.db')):
        messages.error(request, 'Файл не найден')
        return redirect('admin-backups')
    
    response = FileResponse(open(filepath, 'rb'), content_type='application/sql')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Логируем скачивание
    AuditLog.objects.create(
        action='viewed',
        actor=request.user,
        description=f'Администратор {request.user.username} скачал резервную копию: {filename}',
        method='GET',
        ip_address=request.META.get('REMOTE_ADDR'),
        path=request.path,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return response


@admin_required
@require_http_methods(["POST"])
def backup_restore(request, filename):
    """Восстановление из резервной копии"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    if not os.path.exists(filepath) or not filename.endswith(('.sql', '.db')):
        messages.error(request, 'Файл не найден')
        return redirect('admin-backups')
    
    try:
        # Получаем настройки БД
        db_settings = settings.DATABASES['default']
        db_name = db_settings.get('NAME', 'bookstore')
        db_user = db_settings.get('USER', 'bookstore')
        db_host = db_settings.get('HOST', 'localhost')
        db_port = db_settings.get('PORT', '5432')
        db_password = db_settings.get('PASSWORD', '')
        
        # Восстанавливаем из резервной копии
        # Проверяем, используется ли SQLite
        if 'sqlite' in db_settings.get('ENGINE', '').lower():
            # Для SQLite просто копируем файл
            import shutil
            db_path = db_settings.get('NAME')
            if filepath.endswith('.db') and os.path.exists(filepath):
                shutil.copy2(filepath, db_path)
            else:
                raise Exception('Резервная копия SQLite должна быть в формате .db')
            result_code = 0
        else:
            # Для PostgreSQL
            env = os.environ.copy()
            if db_password:
                env['PGPASSWORD'] = db_password
            
            cmd = [
                'psql',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', db_name,
                '-f', filepath
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            result_code = result.returncode
        
        if result_code == 0:
            # Логируем восстановление
            AuditLog.objects.create(
                action='backup_restored',
                actor=request.user,
                description=f'Администратор {request.user.username} восстановил данные из резервной копии: {filename}',
                method='POST',
                ip_address=request.META.get('REMOTE_ADDR'),
                path=request.path,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                new_data={'filename': filename}
            )
            messages.success(request, f'Данные успешно восстановлены из резервной копии: {filename}')
        else:
            error_msg = result.stderr if 'result' in locals() else 'Ошибка восстановления'
            messages.error(request, f'Ошибка при восстановлении: {error_msg}')
    
    except Exception as e:
        messages.error(request, f'Ошибка при восстановлении: {str(e)}')
    
    return redirect('admin-backups')


@admin_required
@require_http_methods(["POST"])
def backup_delete(request, filename):
    """Удаление резервной копии"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    filepath = os.path.join(backup_dir, filename)
    
    if not os.path.exists(filepath) or not filename.endswith(('.sql', '.db')):
        messages.error(request, 'Файл не найден')
        return redirect('admin-backups')
    
    try:
        os.remove(filepath)
        
        # Логируем удаление
        AuditLog.objects.create(
            action='backup_deleted',
            actor=request.user,
            description=f'Администратор {request.user.username} удалил резервную копию: {filename}',
            method='POST',
            ip_address=request.META.get('REMOTE_ADDR'),
            path=request.path,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            old_data={'filename': filename}
        )
        messages.success(request, f'Резервная копия удалена: {filename}')
    
    except Exception as e:
        messages.error(request, f'Ошибка при удалении: {str(e)}')
    
    return redirect('admin-backups')

