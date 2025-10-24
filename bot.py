
import asyncio
import random
import os
import json
import time
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.custom import Button
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.contacts import BlockRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.types import InputPhoto
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

IMAGES_DIR = 'images'
CHANGE_INTERVAL = 5 * 60
USERS_DATA_FILE = 'users_data.json'

def load_users_data():
    """تحميل بيانات المستخدمين من ملف JSON"""
    if os.path.exists(USERS_DATA_FILE):
        try:
            with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'accepted': [], 'blocked': []}
    return {'accepted': [], 'blocked': []}

def save_users_data(data):
    """حفظ بيانات المستخدمين في ملف JSON"""
    with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_random_image():
    """اختيار صورة عشوائية من مجلد الصور"""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    
    images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        raise FileNotFoundError("لا توجد صور في مجلد images")
    return os.path.join(IMAGES_DIR, random.choice(images))

async def change_profile_photo(user_client):
    """تغيير صورة الملف الشخصي للحساب الشخصي"""
    try:
        image_path = get_random_image()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] جاري تغيير صورة الملف الشخصي...")
        print(f"الصورة المختارة: {image_path}")
        
        file = await user_client.upload_file(image_path)
        await user_client(UploadProfilePhotoRequest(file=file))
        
        print(f"✅ تم تغيير صورة الملف الشخصي بنجاح!")
        print("-" * 50)
        
    except FileNotFoundError as e:
        print(f"⚠️  {str(e)}")
        print("يرجى إضافة صور في مجلد 'images' لتفعيل ميزة تغيير الصورة التلقائي")
        print("-" * 50)
    except Exception as e:
        print(f"❌ خطأ أثناء تغيير الصورة: {str(e)}")
        print("-" * 50)

async def main():
    if not API_ID or not API_HASH:
        print("❌ خطأ: يرجى تعيين API_ID و API_HASH")
        return
    
    if not BOT_TOKEN:
        print("❌ خطأ: يرجى تعيين BOT_TOKEN")
        return
    
    print("=" * 50)
    print("بوت تيليجرام المتقدم")
    print("رسائل ترحيب تفاعلية + تغيير صورة تلقائي")
    print("=" * 50)
    print(f"وقت تغيير الصورة: كل {CHANGE_INTERVAL // 60} دقائق")
    
    try:
        images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"عدد الصور المتاحة: {len(images)}")
    except:
        print("⚠️  لا يوجد مجلد صور - سيتم إنشاؤه")
    
    users_data = load_users_data()
    print(f"المستخدمون المقبولون: {len(users_data.get('accepted', []))}")
    print(f"المستخدمون المحظورون: {len(users_data.get('blocked', []))}")
    print("=" * 50)
    
    bot = TelegramClient('bot_session', int(API_ID), API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    
    bot_me = await bot.get_me()
    print(f"✅ تم الاتصال بالبوت: @{bot_me.username}")
    
    user_client = None
    if SESSION_STRING:
        try:
            user_client = TelegramClient(StringSession(SESSION_STRING), int(API_ID), API_HASH)
            await user_client.connect()
            user_me = await user_client.get_me()
            print(f"✅ تم الاتصال بالحساب الشخصي: {user_me.first_name}")
        except Exception as e:
            print(f"⚠️  تعذر الاتصال بالحساب الشخصي: {str(e)}")
            print("ستعمل ميزة الرسائل فقط بدون تغيير الصورة")
    else:
        print("⚠️  لا يوجد SESSION_STRING - ميزة تغيير الصورة معطلة")
    
    print("=" * 50)
    
    # معالج الرسائل الواردة للحساب الشخصي
    if user_client:
        @user_client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def handle_personal_message(event):
            """معالج الرسائل الواردة للحساب الشخصي - يرسل رد تلقائي"""
            sender = await event.get_sender()
            user_id = sender.id
            users_data = load_users_data()
            
            # تجاهل الرسائل من المحظورين
            if user_id in users_data.get('blocked', []):
                print(f"⛔ محاولة رسالة من مستخدم محظور: {sender.first_name} (ID: {user_id})")
                return
            
            # إذا لم يكن مقبولاً، أرسل رسالة الشروط
            if user_id not in users_data.get('accepted', []):
                print(f"📨 رسالة جديدة في الحساب الشخصي من: {sender.first_name} (ID: {user_id})")
                
                welcome_text = f"""مرحباً {sender.first_name}, 
🎯 شروط المحادثة الخاصة بـ مسودن
الحساب مخصص لـ:

``````« بوتات – مواقع – ألعاب »```
📌 الشروط:
1️⃣ يُرجى الالتزام بالاحترام وعدم الإساءة أو التخريب.
2️⃣ يُمنع طلب أي شيء مجاني.
3️⃣ يُمنع منعًا باتًا طلب الصداقة بيني وبينك

✅ للموافقة على الشروط: أرسل كلمة "قبول"
❌ للرفض: أرسل كلمة "رفض"
``````

⚠️ لن يتم الرد حتى تقبل أو ترفض"""
                
                await event.respond(welcome_text)
                return
            
            # المستخدم مقبول - يمكنه المراسلة
            print(f"💬 رسالة من {sender.first_name}: {event.text[:50] if event.text else '[رسالة غير نصية]'}...")
        
        # معالج الردود على رسائل الشروط
        @user_client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def handle_terms_response(event):
            """معالج ردود المستخدمين على الشروط"""
            sender = await event.get_sender()
            user_id = sender.id
            users_data = load_users_data()
            
            if user_id in users_data.get('blocked', []):
                return
            
            if user_id not in users_data.get('accepted', []):
                message_text = event.text.strip() if event.text else ""
                
                # قبول الشروط
                if message_text in ['قبول', 'موافق', 'اقبل', 'نعم']:
                    users_data.setdefault('accepted', []).append(user_id)
                    save_users_data(users_data)
                    
                    await event.respond("✅ تم قبول الشروط بنجاح!\n\nيمكنك الآن إرسال رسالتك.")
                    print(f"✅ المستخدم {sender.first_name} (ID: {user_id}) قبل الشروط")
                
                # رفض الشروط
                elif message_text in ['رفض', 'لا', 'ارفض']:
                    await event.respond("❌ تم رفض الشروط.\n\nسيتم حظر حسابك وحذف المحادثة من الطرفين.")
                    print(f"❌ المستخدم {sender.first_name} (ID: {user_id}) رفض الشروط في المحادثة الخاصة")
                    
                    await asyncio.sleep(1)
                    
                    block_success = False
                    delete_success = False
                    
                    try:
                        # حظر المستخدم
                        await user_client(BlockRequest(sender))
                        block_success = True
                        print(f"🚫 تم حظر المستخدم {user_id}")
                        
                        await asyncio.sleep(0.5)
                        
                        # حذف المحادثة من الطرفين
                        await user_client(DeleteHistoryRequest(
                            peer=sender,
                            max_id=0,
                            just_clear=False,
                            revoke=True
                        ))
                        delete_success = True
                        print(f"🗑️ تم حذف المحادثة مع المستخدم {user_id} من الطرفين")
                        
                    except Exception as e:
                        print(f"⚠️  خطأ أثناء الحظر/الحذف: {str(e)}")
                    
                    # حفظ في قائمة المحظورين
                    if user_id not in users_data.get('blocked', []):
                        users_data.setdefault('blocked', []).append(user_id)
                    if user_id in users_data.get('accepted', []):
                        users_data['accepted'].remove(user_id)
                    save_users_data(users_data)
                    
                    if block_success and delete_success:
                        print(f"✅ العملية مكتملة: حظر + حذف المحادثة للمستخدم {user_id}")
                    elif block_success:
                        print(f"⚠️ تم الحظر فقط (فشل حذف المحادثة)")
                    else:
                        print(f"⚠️ تم الحفظ في قائمة المحظورين محلياً فقط")
    
    @bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handle_bot_message(event):
        """معالج الرسائل الخاصة للبوت (النظام القديم)"""
        sender = await event.get_sender()
        user_id = sender.id
        users_data = load_users_data()
        
        if user_id in users_data.get('blocked', []):
            print(f"⛔ محاولة رسالة من مستخدم محظور في البوت: {sender.first_name} (ID: {user_id})")
            return
        
        if user_id not in users_data.get('accepted', []):
            print(f"📨 رسالة من مستخدم جديد في البوت: {sender.first_name} (ID: {user_id})")
            
            welcome_text = """مرحباً بك في المحادثة الخاصة لـ مسودن،

شروط المحادثة الخاصة
---------------------------------- |
1- لا تذب ميانه  »  تنلبس   |
2- لا تفضفض »  تنلبس       |
3- لا تطلب صور »  تنلبس   |
4- لا تطلب صوت»  تنلبس   |
5- لتطلب اتصال»  تنلبس    |
---------------------------------- |"""
            
            buttons = [
                [Button.inline("✅ قبول", b"accept_terms")],
                [Button.inline("❌ رفض", b"reject_terms")]
            ]
            
            await event.respond(welcome_text, buttons=buttons)
            return
        
        print(f"💬 رسالة في البوت من {sender.first_name}: {event.text[:50] if event.text else '[رسالة غير نصية]'}...")
    
    @bot.on(events.CallbackQuery())
    async def handle_callback(event):
        """معالج الأزرار التفاعلية للبوت"""
        sender = await event.get_sender()
        user_id = sender.id
        users_data = load_users_data()
        
        if event.data == b"accept_terms":
            if user_id not in users_data.get('accepted', []):
                users_data.setdefault('accepted', []).append(user_id)
                save_users_data(users_data)
                
                await event.edit("✅ تم قبول الشروط بنجاح!\n\nيمكنك الآن إرسال رسالتك.")
                print(f"✅ المستخدم {sender.first_name} (ID: {user_id}) قبل الشروط في البوت")
            else:
                await event.answer("لقد قبلت الشروط مسبقاً", alert=False)
        
        elif event.data == b"reject_terms":
            await event.edit("❌ تم رفض الشروط.\n\nسيتم حظر حسابك وحذف المحادثة من الطرفين.")
            print(f"❌ المستخدم {sender.first_name} (ID: {user_id}) رفض الشروط في البوت")
            
            block_success = False
            delete_success = False
            
            if user_client:
                try:
                    await asyncio.sleep(1)
                    
                    try:
                        input_user = await bot.get_input_entity(user_id)
                    except:
                        input_user = sender
                    
                    # حظر المستخدم
                    await user_client(BlockRequest(input_user))
                    block_success = True
                    print(f"🚫 تم حظر المستخدم {user_id} من الحساب الشخصي")
                    
                    await asyncio.sleep(0.5)
                    
                    # حذف المحادثة من الطرفين
                    await user_client(DeleteHistoryRequest(
                        peer=input_user,
                        max_id=0,
                        just_clear=False,
                        revoke=True
                    ))
                    delete_success = True
                    print(f"🗑️ تم حذف المحادثة مع المستخدم {user_id} من الطرفين")
                    
                except Exception as e:
                    print(f"⚠️  خطأ أثناء الحظر/الحذف: {str(e)}")
                    print(f"   سيتم حفظ المستخدم في قائمة المحظورين بدون حظر فعلي")
            else:
                print(f"⚠️  لا يمكن تنفيذ الحظر - الحساب الشخصي غير متصل")
            
            # حفظ في قائمة المحظورين
            if user_id not in users_data.get('blocked', []):
                users_data.setdefault('blocked', []).append(user_id)
            if user_id in users_data.get('accepted', []):
                users_data['accepted'].remove(user_id)
            save_users_data(users_data)
            
            if block_success and delete_success:
                print(f"✅ العملية مكتملة: حظر + حذف المحادثة للمستخدم {user_id}")
            elif block_success:
                print(f"⚠️ تم الحظر فقط (فشل حذف المحادثة)")
            else:
                print(f"⚠️ تم الحفظ في قائمة المحظورين محلياً فقط")
    
    print("🤖 البوت يعمل الآن...")
    print("⏳ في انتظار الرسائل...")
    print("-" * 50)
    
    if user_client:
        try:
            await change_profile_photo(user_client)
        except:
            pass
        
        async def photo_changer():
            """مهمة تغيير الصورة بشكل دوري"""
            while True:
                await asyncio.sleep(CHANGE_INTERVAL)
                try:
                    await change_profile_photo(user_client)
                except:
                    pass
        
        asyncio.create_task(photo_changer())
    
    await bot.run_until_disconnected()
    
    if user_client:
        await user_client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  تم إيقاف البرنامج")
