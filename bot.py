import asyncio
import random
import os
import time
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.types import InputPhoto
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING', '')

IMAGES_DIR = 'images'
CHANGE_INTERVAL = 5 * 60

def get_random_image():
    images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        raise FileNotFoundError("لا توجد صور في مجلد images")
    return os.path.join(IMAGES_DIR, random.choice(images))

async def change_profile_photo(client):
    try:
        image_path = get_random_image()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] جاري تغيير صورة الملف الشخصي...")
        print(f"الصورة المختارة: {image_path}")
        
        file = await client.upload_file(image_path)
        await client(UploadProfilePhotoRequest(file=file))
        
        print(f"✅ تم تغيير صورة الملف الشخصي بنجاح!")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ خطأ أثناء تغيير الصورة: {str(e)}")
        print("-" * 50)

async def main():
    if not API_ID or not API_HASH:
        print("❌ خطأ: يرجى تعيين API_ID و API_HASH")
        return
    
    if not SESSION_STRING:
        print("❌ خطأ: يرجى تعيين SESSION_STRING")
        return
    
    print("=" * 50)
    print("برنامج تغيير صورة الملف الشخصي على تيليجرام")
    print("=" * 50)
    print(f"وقت التغيير: كل {CHANGE_INTERVAL // 60} دقائق")
    print(f"عدد الصور المتاحة: {len([f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))])}")
    print("=" * 50)
    
    async with TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH) as client:
        print(f"✅ تم الاتصال بحساب: {(await client.get_me()).first_name}")
        print("=" * 50)
        
        await change_profile_photo(client)
        
        while True:
            await asyncio.sleep(CHANGE_INTERVAL)
            await change_profile_photo(client)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف البرنامج")
