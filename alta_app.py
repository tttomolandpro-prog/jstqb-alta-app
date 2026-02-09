import streamlit as st
import json
import random

# ページ設定
st.set_page_config(page_title="ALTA特訓マシーン", layout="centered")

# スマホ向けCSS
st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 3.5em; margin-bottom: 10px; font-size: 1.1em; }
    .stProgress > div > div > div > div { background-color: #e67e22; }
    </style>
    """, unsafe_allow_html=True)

# データの読み込み
@st.cache_data
def load_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        return json.load(f)

all_qs = load_questions()

# セッション状態（履歴など）の初期化
if 'quiz_set' not in st.session_state:
    st.session_state.quiz_set = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.game_over = False

# クイズ開始関数
def start_balanced_quiz():
    ch3 = [q for q in all_qs if str(q['chapter']) == "3"]
    others = [q for q in all_qs if str(q['chapter']) != "3"]
    
    selected_ch3 = random.sample(ch3, min(len(ch3), 20))
    selected_others = random.sample(others, min(len(others), 20))
    
    st.session_state.quiz_set = selected_ch3 + selected_others
    random.shuffle(st.session_state.quiz_set)
    
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.game_over = False

# メインUI
st.title("🔥 ALTA合格特訓")

if not st.session_state.quiz_set:
    st.write("第3章(20問)と他の章(20問)を組み合わせて出題します。")
    if st.button("特訓モードを開始する"):
        start_balanced_quiz()
        st.rerun()

elif not st.session_state.game_over:
    q = st.session_state.quiz_set[st.session_state.current_idx]
    
    # 進捗
    progress = (st.session_state.current_idx) / len(st.session_state.quiz_set)
    st.progress(progress)
    st.write(f"問題 {st.session_state.current_idx + 1} / {len(st.session_state.quiz_set)}")
    
    st.subheader(q['question'])
    
    # 回答ボタン
    for opt in q['options']:
        if st.button(opt, key=f"opt_{st.session_state.current_idx}_{opt}"):
            if opt == q['answer']:
                st.session_state.score += 1
                st.success("正解！")
            else:
                st.session_state.wrong_list.append(q)
                st.error(f"不正解... 正解は: {q['answer']}")
            
            st.session_state.current_idx += 1
            if st.session_state.current_idx >= len(st.session_state.quiz_set):
                st.session_state.game_over = True
            st.rerun()

else:
    # 結果表示
    percent = (st.session_state.score / len(st.session_state.quiz_set)) * 100
    st.balloons()
    st.header(f"結果: {percent:.1f}%")
    st.write(f"正解数: {st.session_state.score} / {len(st.session_state.quiz_set)}")
    
    if st.session_state.wrong_list:
        st.warning(f"間違えた問題が {len(st.session_state.wrong_list)} 問あります。")
        if st.button("❌ 間違えた問題だけ再挑戦"):
            st.session_state.quiz_set = st.session_state.wrong_list.copy()
            st.session_state.current_idx = 0
            st.session_state.score = 0
            st.session_state.wrong_list = []
            st.session_state.game_over = False
            st.rerun()
            
    if st.button("🏠 最初からやり直す"):
        start_balanced_quiz()
        st.rerun()
