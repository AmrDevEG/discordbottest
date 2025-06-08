import discord
from discord.ext import commands
import random

# ------------------- الإعدادات الأساسية -------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True # هذه الصلاحية ضرورية جداً لنظام الترحيب

bot = commands.Bot(command_prefix='!', intents=intents)

# ------------------- الأحداث (Events) -------------------
@bot.event
async def on_ready():
    print('-----------------------------------------')
    print(f'البوت اشتغل بنجاح باسم: {bot.user.name}')
    print('-----------------------------------------')
    await bot.change_presence(activity=discord.Game(name="!help لمشاهدة الأوامر"))

# --- الحدث الجديد: الترحيب بالأعضاء الجدد وإعطاء الرتبة ---
@bot.event
async def on_member_join(member):
    # أولاً: البحث عن قناة الترحيب بالاسم (غير "welcome" لو اسم القناة عندك مختلف)
    welcome_channel = discord.utils.get(member.guild.channels, name='welcome')
    
    # ثانياً: البحث عن الرتبة بالاسم (غير "Member" لو اسم الرتبة عندك مختلف)
    member_role = discord.utils.get(member.guild.roles, name='Member')

    if not welcome_channel:
        print("خطأ: لم أجد قناة باسم 'welcome'")
        return
    if not member_role:
        print("خطأ: لم أجد رتبة باسم 'Member'")
        return

    # ثالثاً: إعطاء الرتبة للعضو الجديد
    try:
        await member.add_roles(member_role)
        print(f"تم إعطاء رتبة {member_role.name} للعضو {member.name}")
    except discord.Forbidden:
        print(f"خطأ: ليس لدي صلاحية لإعطاء رتبة {member_role.name}. تأكد من ترتيب الرتب.")

    # رابعاً: إنشاء رسالة الترحيب الاحترافية (Embed)
    embed = discord.Embed(
        title=f"🎉 عضو جديد انضم إلينا! 🎉",
        description=f"أهلاً بك يا {member.mention} في سيرفر **{member.guild.name}**!\n\nنورت السيرفر بوجودك، نتمنى لك وقتاً ممتعاً معنا.",
        color=discord.Color.from_rgb(0, 255, 255) # لون سماوي فاتح
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_image(url="https://i.gifer.com/origin/e0/e03c276c1173254924151a70c5240a5a_w200.gif")
    embed.add_field(name="أنت الآن العضو رقم:", value=f"**#{member.guild.member_count}**", inline=False)
    embed.set_footer(text="نتمنى لك أفضل الأوقات!", icon_url=member.guild.icon.url)
    await welcome_channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('🤔 الأمر ده مش موجود. جرب تكتب `!help`')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('🚫 معندكش الصلاحية عشان تستخدم الأمر ده.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('🤔 أنت نسيت تكتب حاجة مهمة مع الأمر. شوف `!help` عشان تعرف طريقة الاستخدام الصح.')
    else:
        print(error)
        await ctx.send('حدث خطأ غير متوقع أثناء تنفيذ الأمر.')

# ------------------- الأوامر (Commands) -------------------

# الأمر 1: ترحيب
@bot.command(name='hello', help='البوت بيرد عليك التحية.')
async def hello_command(ctx):
    await ctx.send(f'أهلاً بك يا {ctx.author.mention}!')

# الأمر 2: تكرار الكلام
@bot.command(name='say', help='البوت بيكرر الكلام اللي تكتبه.')
async def say_command(ctx, *, text_to_say: str):
    await ctx.send(text_to_say)

# الأمر 3: إرسال رسالة لقناة محددة
@bot.command(name='send', help='يرسل رسالة إلى قناة محددة.\nالاستخدام: !send #channel <your_message>')
@commands.has_permissions(manage_messages=True)
async def send_to_channel(ctx, channel: discord.TextChannel, *, message: str):
    try:
        await channel.send(message)
        await ctx.send(f'✅ تم إرسال رسالتك بنجاح إلى القناة {channel.mention}')
    except discord.Forbidden:
        await ctx.send(f'❌ ليس لدي صلاحية للكتابة في القناة {channel.mention}.')

# الأمر 4: إرسال صورة لقناة محددة
@bot.command(name='sendpic', help='يرسل صورة مرفقة إلى قناة محددة.\nالاستخدام: !sendpic #channel (مع رفع الصورة)')
@commands.has_permissions(manage_messages=True)
async def send_pic_command(ctx, channel: discord.TextChannel):
    if not ctx.message.attachments:
        return await ctx.send('❌ أنت لم ترفق أي صورة مع الأمر!')
    try:
        file = await ctx.message.attachments[0].to_file()
        await channel.send(file=file)
        await ctx.send(f'🖼️ تم إرسال الصورة بنجاح إلى القناة {channel.mention}')
    except discord.Forbidden:
        await ctx.send(f'❌ ليس لدي صلاحية لإرسال ملفات في القناة {channel.mention}.')

# الأمر 5: إرسال رسالة وصورة معًا
@bot.command(name='sendmsgpic', help='يرسل رسالة وصورة معًا إلى قناة محددة.\nالاستخدام: !sendmsgpic #channel <your_message> (مع رفع الصورة)')
@commands.has_permissions(manage_messages=True)
async def send_msg_pic_command(ctx, channel: discord.TextChannel, *, message: str):
    if not ctx.message.attachments:
        return await ctx.send('❌ أنت لم ترفق أي صورة مع الأمر!')
    try:
        file = await ctx.message.attachments[0].to_file()
        await channel.send(content=message, file=file)
        await ctx.send(f'✅🖼️ تم إرسال الرسالة والصورة بنجاح إلى القناة {channel.mention}')
    except discord.Forbidden:
        await ctx.send(f'❌ ليس لدي صلاحية لإرسال ملفات في القناة {channel.mention}.')

# الأمر 6: رمي النرد
@bot.command(name='roll', help='بيرمي نرد وبيديك رقم عشوائي من 1 إلى 6.')
async def roll_command(ctx):
    number = random.randint(1, 6)
    await ctx.send(f'🎲 رميت النرد وطلعلك رقم **{number}**!')

# الأمر 7: مسح الرسائل
@bot.command(name='clear', help='لحذف عدد معين من الرسائل.\nالاستخدام: !clear 5')
@commands.has_permissions(manage_messages=True)
async def clear_command(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🧹 تم حذف **{amount}** من الرسائل بنجاح!', delete_after=5)

# ------------------- تشغيل البوت -------------------
TOKEN = "MTM4MTMyNDI0MTIxOTIyNzY0OA.Gk2s2y.S6DskiyA8hfANEEy36mxonZQHs3UymC4xlcMbo"
bot.run(TOKEN)