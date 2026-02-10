import streamlit as st
import json
import random

# 1. ページ基本設定（スマホのブラウザで見た時に最適化）
st.set_page_config(page_title="JSTQB ALTA特訓", layout="centered")

# 2. スマホ用カスタムCSS（ボタンを大きくし、解説を読みやすく）
st.markdown("""
    <style>
    /* ボタンを大きく押しやすく */
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        margin-bottom: 10px;
        font-size: 1.1em;
        border-radius: 10px;
    }
    /* プログレスバーの色 */
    .stProgress > div > div > div > div {
        background-color: #e67e22;
    }
    /* 解説エリアの装飾 */
    .explanation-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #3498db;
        line-height: 1.6;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 問題データの読み込み（キャッシュを利用）
@st.cache_data
def load_questions():
    try:
        with open('questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"JSONの読み込みに失敗しました。構文を確認してください。: {e}")
        return []

all_qs = load_questions()

# 4. セッション状態の初期化
if 'quiz_set' not in st.session_state:
    st.session_state.quiz_set = []
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.game_over = False
    st.session_state.answered = False # 回答済みかどうか
    st.session_state.last_result = "" # 正解/不正解メッセージ

# クイズ開始ロジック（3章:20問 + 他:20問）
def start_balanced_quiz():
    ch3 = [q for q in all_qs if str(q.get('chapter')) == "3"]
    others = [q for q in all_qs if str(q.get('chapter')) != "3"]
    
    # 3章から最大20問、他から最大20問をランダム抽出
    s_ch3 = random.sample(ch3, min(len(ch3), 20))
    s_others = random.sample(others, min(len(others), 20))
    
    st.session_state.quiz_set = s_ch3 + s_others
    random.shuffle(st.session_state.quiz_set)
    
    # 全変数のリセット
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.wrong_list = []
    st.session_state.game_over = False
    st.session_state.answered = False

# --- メイン画面描画 ---
st.title("🔥 ALTA合格特訓モード")

# A. 初期画面（まだ問題がセットされていない）
if not st.session_state.quiz_set:
    st.info("第3章（テスト技法）20問 ＋ 他の章 20問の合計40問を出題します。")
    if st.button("特訓を開始する"):
        start_balanced_quiz()
        st.rerun()

# B. クイズ進行中
elif not st.session_state.game_over:
    q = st.session_state.quiz_set[st.session_state.current_idx]
    
    # 進捗表示
    total = len(st.session_state.quiz_set)
    curr = st.session_state.current_idx + 1
    st.progress(curr / total)
    st.caption(f"問題 {curr} / {total}  (現在の正解数: {st.session_state.score})")
    
    # 問題文
    st.subheader(q['question'])
    
    # B-1. まだ回答していない状態：選択肢ボタンを表示
    if not st.session_state.answered:
        for opt in q['options']:
            if st.button(opt, key=f"btn_{curr}_{opt}"):
                st.session_state.answered = True
                if opt == q['answer']:
                    st.session_state.score += 1
                    st.session_state.last_result = "✅ **正解！**"
                else:
                    st.session_state.wrong_list.append(q)
                    st.session_state.last_result = f"❌ **不正解...** (正解: {q['answer']})"
                st.rerun()
    
    # B-2. 回答済みの状態：結果と解説を表示
    else:
        if "✅" in st.session_state.last_result:
            st.success(st.session_state.last_result)
        else:
            st.error(st.session_state.last_result)
        
        # 解説をボックスで表示
        st.markdown(f"""
            <div class="explanation-box">
                <strong>💡 解説:</strong><br>
                {q.get('explanation', '解説はありません。')}
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("次の問題へ ➔"):
            st.session_state.answered = False
            st.session_state.current_idx += 1
            if st.session_state.current_idx >= len(st.session_state.quiz_set):
                st.session_state.game_over = True
            st.rerun()

# C. 結果表示画面
else:
    total_q = len(st.session_state.quiz_set)
    percent = (st.session_state.score / total_q) * 100
    st.balloons()
    st.header(f"🏁 スコア: {percent:.1f}%")
    st.write(f"結果: {total_q}問中 {st.session_state.score}問 正解")
    
    # 間違えた問題がある場合のみ「再挑戦」ボタンを出す
    if st.session_state.wrong_list:
        wrong_count = len(st.session_state.wrong_list)
        st.warning(f"間違えた問題が {wrong_count} 問あります。")
        if st.button(f"❌ 間違えた {wrong_count} 問だけ再挑戦"):
            # 抽出セットを間違いリストに差し替える
            st.session_state.quiz_set = st.session_state.wrong_list.copy()
            st.session_state.current_idx = 0
            st.session_state.score = 0
            st.session_state.wrong_list = []
            st.session_state.game_over = False
            st.session_state.answered = False
            st.rerun()
            
    if st.button("🏠 最初からやり直す（全40問）"):
        start_balanced_quiz()
        st.rerun()

