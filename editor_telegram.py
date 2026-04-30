from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler ,ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv 
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
import img2pdf 
from pdf2docx import Converter
from docx2pdf import convert
from pdf2image import convert_from_path


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
user_mode = {}
user_images = {}
os.makedirs("temp", exist_ok=True)
os.makedirs("processed", exist_ok=True)
SUBSCRIBE_LINK = "https://www.youtube.com/@elsayed_hassann"
allowed_users = set()

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi I'm a background removal bot, to start click on /start ")
    
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in allowed_users:
        keyboard = [["اشتراك في القناة"], ["تم الاشتراك"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"لازم تشترك الأول 👇\n{SUBSCRIBE_LINK}",
            reply_markup=reply_markup
    )
        return
    keyboard = [
    ["Remove Background"],
    ["Enhance (Simple)"],
    ["Image → PDF"],
    ["PDF → Word"],
    ["PDF → Images"],
    ["Word → PDF"],
    ["Finish Images"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "اختار الخدمة 👇",
        reply_markup=reply_markup
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🤖 **أهلاً بيك!** البوت بيوفرلك أدوات سريعة للصور والملفات 👇📸 إزالة خلفية الصور✨ تحسين الصور🖼️ تحويل صور إلى PDF (استخدم Finish Images بعد ما تخلص)📄 PDF ⇄ Word🖼️ PDF → صور⚡ اختار من الأزرار وابعت الملف المناسب لكل خدمة وابدأ فورًا 🚀")

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if text == "تم الاشتراك":
        allowed_users.add(chat_id)
        await update.message.reply_text("تمام ✅ اضغط /start واستمتع بالخدمات")
        return

    if chat_id not in allowed_users:
        await update.message.reply_text("اشترك الأول في القناة ❌")
        return

    if text == "Remove Background":
        user_mode[chat_id] = "bg"
        await update.message.reply_text("ابعت الصورة لإزالة الخلفية 📸")

    elif text == "Enhance (Simple)":
        user_mode[chat_id] = "enhance"
        await update.message.reply_text("ابعت الصورة لتحسينها ✨")

    elif text == "Image → PDF":
        user_mode[chat_id] = "img2pdf"
        user_images[chat_id] = []
        await update.message.reply_text("ابعت الصور واحدة واحدة، ولما تخلص اضغط Finish Images")

    elif text == "PDF → Word":
        user_mode[chat_id] = "pdf2word"
        await update.message.reply_text("ابعت ملف PDF 📄")

    elif text == "Word → PDF":
        user_mode[chat_id] = "word2pdf"
        await update.message.reply_text("ابعت ملف Word 📄")
    elif text == "PDF → Images":
        user_mode[chat_id] = "pdf2img"
        await update.message.reply_text("ابعت ملف PDF 📄")
    elif text == "Finish Images":
        images = user_images.get(chat_id, [])

        if not images:
            await update.message.reply_text("مفيش صور ❌")
            return

        output_path = f'./processed/{chat_id}.pdf'

        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(images))

        with open(output_path, "rb") as f:
            await update.message.reply_document(f)

    # تنظيف
        for img in images:
            if os.path.exists(img):
                os.remove(img)

        if os.path.exists(output_path):
            os.remove(output_path)

        user_images[chat_id] = []
        user_mode[chat_id] = None

        await update.message.reply_text("تم التحويل ✅")
        return
        
async def process_image(photo_name:str):
    name, _ = os.path.splitext(photo_name)
    output_photo_path = f'./processed/{name}.png'
    input=Image.open(f'./temp/{photo_name}')
    output=remove(input)
    output.save(output_photo_path)
    return output_photo_path
    
async def enhance_image(photo_name):
    input_path = f'./temp/{photo_name}'
    output_path = f'./processed/enhanced_{photo_name}'

    img = Image.open(input_path)

    # 🟢 تكبير الصورة
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)

    # 🟢 زيادة الحدة (Sharpness)
    sharp = ImageEnhance.Sharpness(img)
    img = sharp.enhance(2.0)

    # 🟢 تحسين الكونتراست
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.3)

    # 🟢 تحسين الإضاءة
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.1)

    # 🟢 فلتر تفاصيل
    img = img.filter(ImageFilter.DETAIL)

    img.save(output_path)

    return output_path
def image_to_pdf(photo_name):
    input_path = f'./temp/{photo_name}'
    output_path = f'./processed/{photo_name}.pdf'

    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(input_path))

    return output_path
def pdf_to_word(file_name):
    input_path = f'./temp/{file_name}'
    output_path = f'./processed/{file_name}.docx'

    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()

    return output_path
def word_to_pdf(file_name):
    input_path = f'./temp/{file_name}'
    output_path = f'./processed/{file_name}.pdf'

    convert(input_path, output_path)

    return output_path
def pdf_to_images(file_name):
    input_path = f'./temp/{file_name}'
    images = convert_from_path(input_path, dpi=150, poppler_path=r"C:\poppler-25.12.0\Library\bin")

    paths = []
    for i, img in enumerate(images):
        path = f'./processed/{file_name}_{i}.jpg'
        img.save(path, "JPEG")
        paths.append(path)

    return paths
async def remove_background(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    mode = user_mode.get(chat_id)
    if not (update.message.photo or update.message.document):
            return

    if not mode:
        await update.message.reply_text("اختار الأول من /start")
        return

    if update.message.photo:
        import uuid
        photo_name = f"{uuid.uuid4()}.jpg"
        file = await update.message.photo[-1].get_file()
    else:
        import uuid
        
        file_name = update.message.document.file_name or "file"
        _, ext = os.path.splitext(file_name)
        photo_name = f"{uuid.uuid4()}{ext}"
        file = await update.message.document.get_file()

    path = f'./temp/{photo_name}'

    await file.download_to_drive(path)
    await update.message.reply_text("Processing... ⏳")

    result = None

    try:
        if mode == "bg":
            result = await process_image(photo_name)

        elif mode == "enhance":
            result = await enhance_image(photo_name)

        elif mode == "img2pdf":
            user_images.setdefault(chat_id, []).append(path)
            await update.message.reply_text("تم إضافة الصورة 👍 ابعت كمان أو اضغط Finish Images")
            return

        elif mode == "pdf2word":
            result =  pdf_to_word(photo_name)
        elif mode == "pdf2img":
            results = pdf_to_images(photo_name)

            for p in results:
                with open(p, "rb") as f:
                    await update.message.reply_photo(photo=f)

            for p in results:
                os.remove(p)
            return

        elif mode == "word2pdf":
            result =  word_to_pdf(photo_name)

        if result:
            with open(result, 'rb') as f:
                await update.message.reply_document(f)

    finally:
        # 🧹 تنظيف آمن
        if mode != "img2pdf" and os.path.exists(path):
            os.remove(path)
        if result and os.path.exists(result):
            os.remove(result)

if __name__=='__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    #command handlers
    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    
    #registering handlers
    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, remove_background))
    
    application.run_polling()