import streamlit as st
import time
import random
from io import BytesIO

# --- 1. 核心相容性修復 ---
def safe_rerun():
    """自動判斷並執行重整"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except:
            st.stop()

def safe_play_audio(text):
    """語音播放安全模式"""
    try:
        from gtts import gTTS
        # 使用印尼語 (id) 發音
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp, format='audio/mp3')
    except Exception as e:
        st.caption(f"🔇 (語音生成暫時無法使用)")

# --- 0. 系統配置 ---
st.set_page_config(page_title="Unit 27: O Demak", page_icon="🏃", layout="centered")

# --- CSS 美化 (活力洋紅色調) ---
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .source-tag { font-size: 12px; color: #aaa; text-align: right; font-style: italic; }
    
    /* 單字卡 */
    .word-card {
        background: linear-gradient(135deg, #F3E5F5 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 4px solid #AB47BC;
    }
    .emoji-icon { font-size: 48px; margin-bottom: 10px; }
    .amis-text { font-size: 22px; font-weight: bold; color: #7B1FA2; }
    .chinese-text { font-size: 16px; color: #7f8c8d; }
    
    /* 句子框 */
    .sentence-box {
        background-color: #F3E5F5;
        border-left: 5px solid #CE93D8;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
    }

    /* 按鈕 */
    .stButton>button {
        width: 100%; border-radius: 12px; font-size: 20px; font-weight: 600;
        background-color: #E1BEE7; color: #4A148C; border: 2px solid #AB47BC; padding: 12px;
    }
    .stButton>button:hover { background-color: #BA68C8; border-color: #7B1FA2; }
    .stProgress > div > div > div > div { background-color: #AB47BC; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料庫 (Unit 27: 14個單字 - 句子提取核心詞) ---
vocab_data = [
    {"amis": "Mi'aca", "chi": "買", "icon": "🛍️", "source": "Row 225"},
    {"amis": "Mi'adop", "chi": "打獵", "icon": "🏹", "source": "Row 380"},
    {"amis": "Mipalo", "chi": "揍 / 打", "icon": "👊", "source": "Row 385"},
    {"amis": "Miseti'", "chi": "打 / 鞭打", "icon": "🏏", "source": "Row 211"},
    {"amis": "Miharateng", "chi": "想 / 思考", "icon": "🤔", "source": "Row 319"},
    {"amis": "Misa'icel", "chi": "努力 / 加油", "icon": "💪", "source": "Row 326"},
    {"amis": "Masasowal", "chi": "聊天 / 互說", "icon": "🗣️", "source": "Row 402"},
    {"amis": "Mahakelong", "chi": "一起 / 結伴", "icon": "👫", "source": "Row 485"},
    {"amis": "Milifet", "chi": "測驗 / 比賽", "icon": "📝", "source": "Row 473"},
    {"amis": "Comikay", "chi": "跑 / 賽跑", "icon": "🏃", "source": "Row 983"},
    {"amis": "Payso", "chi": "錢", "icon": "💰", "source": "Row 461"},
    {"amis": "Lotok", "chi": "山", "icon": "⛰️", "source": "Row 380"},
    {"amis": "Dateng", "chi": "菜 / 蔬菜", "icon": "🥬", "source": "Row 225"},
    {"amis": "Harateng", "chi": "想法 / 心意", "icon": "💭", "source": "Row 1084"},
]

# --- 句子庫 (7句: 嚴格源自 CSV 並移除連字號) ---
sentences = [
    {"amis": "Mi'aca ci Panay to titi ato dateng.", "chi": "Panay買肉和菜。", "icon": "🛍️", "source": "Row 225"},
    {"amis": "Mi'adop ci mama i lotok.", "chi": "爸爸在山上打獵。", "icon": "🏹", "source": "Row 380"},
    {"amis": "Miharatengay kako to misowalan no miso i nacila.", "chi": "我想著你昨天所說的話。", "icon": "🤔", "source": "Row 319"},
    {"amis": "Mipalo ko kapah no niyaro' takowanan.", "chi": "部落的青年揍我。", "icon": "👊", "source": "Row 385"},
    {"amis": "Masasowal ko mato'asay.", "chi": "老人互相聊天。", "icon": "🗣️", "source": "Row 402"},
    {"amis": "Mahakelong kita a tayra i pitilidan anocila.", "chi": "我們明天一起去學校。", "icon": "👫", "source": "Row 485"},
    {"amis": "Misa'icel kako a mitilid, 'arawhani, tatiih ko pilifet.", "chi": "我很努力讀書，其實呢，考試不理想。", "icon": "📝", "source": "Row 473"},
]

# --- 3. 隨機題庫 (Synced) ---
raw_quiz_pool = [
    {
        "q": "Mi'aca ci Panay to titi ato dateng.",
        "audio": "Mi'aca ci Panay to titi ato dateng",
        "options": ["Panay買肉和菜", "Panay煮肉和菜", "Panay吃肉和菜"],
        "ans": "Panay買肉和菜",
        "hint": "Mi'aca (買) (Row 225)"
    },
    {
        "q": "Miharatengay kako to misowalan no miso...",
        "audio": "Miharatengay kako to misowalan no miso",
        "options": ["我想著你說的話", "我聽著你說的話", "我看著你說的話"],
        "ans": "我想著你說的話",
        "hint": "Miharateng (想) (Row 319)"
    },
    {
        "q": "單字測驗：Mipalo",
        "audio": "Mipalo",
        "options": ["揍/打", "罵", "笑"],
        "ans": "揍/打",
        "hint": "Row 385: Mipalo ko kapah... (青年揍我)"
    },
    {
        "q": "單字測驗：Masasowal",
        "audio": "Masasowal",
        "options": ["聊天/互說", "吵架", "唱歌"],
        "ans": "聊天/互說",
        "hint": "Row 402: 老人在一起 Masasowal"
    },
    {
        "q": "Mahakelong kita a tayra i pitilidan.",
        "audio": "Mahakelong kita a tayra i pitilidan",
        "options": ["我們一起去學校", "我們各自去學校", "我們不想去學校"],
        "ans": "我們一起去學校",
        "hint": "Mahakelong (一起/結伴) (Row 485)"
    },
    {
        "q": "單字測驗：Mi'adop",
        "audio": "Mi'adop",
        "options": ["打獵", "捕魚", "種田"],
        "ans": "打獵",
        "hint": "Row 380: 爸爸在山上 Mi'adop"
    },
    {
        "q": "單字測驗：Payso",
        "audio": "Payso",
        "options": ["錢", "票", "卡"],
        "ans": "錢",
        "hint": "Row 461: Awaay ko payso (沒有錢)"
    },
    {
        "q": "單字測驗：Misa'icel",
        "audio": "Misa'icel",
        "options": ["努力/加油", "放棄", "休息"],
        "ans": "努力/加油",
        "hint": "Row 326: 要 Misa'icel 才會知道"
    }
]

# --- 4. 狀態初始化 (洗牌邏輯) ---
if 'init' not in st.session_state:
    st.session_state.score = 0
    st.session_state.current_q_idx = 0
    st.session_state.quiz_id = str(random.randint(1000, 9999))
    
    # 抽題與洗牌
    selected_questions = random.sample(raw_quiz_pool, 3)
    final_questions = []
    for q in selected_questions:
        q_copy = q.copy()
        shuffled_opts = random.sample(q['options'], len(q['options']))
        q_copy['shuffled_options'] = shuffled_opts
        final_questions.append(q_copy)
        
    st.session_state.quiz_questions = final_questions
    st.session_state.init = True

# --- 5. 主介面 ---
st.markdown("<h1 style='text-align: center; color: #7B1FA2;'>Unit 27: O Demak</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>行為與事件 (From Sentences)</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📚 詞彙與句型", "🎲 隨機挑戰"])

# === Tab 1: 學習模式 ===
with tab1:
    st.subheader("📝 核心單字 (從句子提取)")
    col1, col2 = st.columns(2)
    for i, word in enumerate(vocab_data):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="word-card">
                <div class="emoji-icon">{word['icon']}</div>
                <div class="amis-text">{word['amis']}</div>
                <div class="chinese-text">{word['chi']}</div>
                <div class="source-tag">src: {word['source']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 聽發音", key=f"btn_vocab_{i}"):
                safe_play_audio(word['amis'])

    st.markdown("---")
    st.subheader("🗣️ 實用句型 (Data-Driven)")
    for i, s in enumerate(sentences):
        st.markdown(f"""
        <div class="sentence-box">
            <div style="font-size: 20px; font-weight: bold; color: #7B1FA2;">{s['icon']} {s['amis']}</div>
            <div style="font-size: 16px; color: #555; margin-top: 5px;">{s['chi']}</div>
            <div class="source-tag">src: {s['source']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ 播放句型", key=f"btn_sent_{i}"):
            safe_play_audio(s['amis'])

# === Tab 2: 隨機挑戰模式 ===
with tab2:
    st.markdown("### 🎲 隨機評量")
    
    if st.session_state.current_q_idx < len(st.session_state.quiz_questions):
        q_data = st.session_state.quiz_questions[st.session_state.current_q_idx]
        
        st.progress((st.session_state.current_q_idx) / 3)
        st.markdown(f"**Question {st.session_state.current_q_idx + 1} / 3**")
        
        st.markdown(f"### {q_data['q']}")
        if q_data['audio']:
            if st.button("🎧 播放題目音檔", key=f"btn_audio_{st.session_state.current_q_idx}"):
                safe_play_audio(q_data['audio'])
        
        # 使用洗牌後的選項
        unique_key = f"q_{st.session_state.quiz_id}_{st.session_state.current_q_idx}"
        user_choice = st.radio("請選擇正確答案：", q_data['shuffled_options'], key=unique_key)
        
        if st.button("送出答案", key=f"btn_submit_{st.session_state.current_q_idx}"):
            if user_choice == q_data['ans']:
                st.balloons()
                st.success("🎉 答對了！")
                time.sleep(1)
                st.session_state.score += 100
                st.session_state.current_q_idx += 1
                safe_rerun()
            else:
                st.error(f"不對喔！提示：{q_data['hint']}")
                
    else:
        st.progress(1.0)
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background-color: #E1BEE7; border-radius: 20px; margin-top: 20px;'>
            <h1 style='color: #7B1FA2;'>🏆 挑戰成功！</h1>
            <h3 style='color: #333;'>本次得分：{st.session_state.score}</h3>
            <p>你已經學會描述各種事件了！</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再來一局 (重新抽題)", key="btn_restart"):
            st.session_state.score = 0
            st.session_state.current_q_idx = 0
            st.session_state.quiz_id = str(random.randint(1000, 9999))
            
            new_questions = random.sample(raw_quiz_pool, 3)
            final_qs = []
            for q in new_questions:
                q_copy = q.copy()
                shuffled_opts = random.sample(q['options'], len(q['options']))
                q_copy['shuffled_options'] = shuffled_opts
                final_qs.append(q_copy)
            
            st.session_state.quiz_questions = final_qs
            safe_rerun()
