import streamlit as st
import json
import os

# ファイルの読み込み
def load_data():
    if os.path.exists('questions.json'):
        with open('questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

st.set_page_config(page_title="JSTQB ALTA 400問マスター", layout="centered")

st.title("🛡️ JSTQB ALTA 合格への400問")
st.caption("シラバス完全準拠・章別問題集")

quiz_data = load_data()

if not quiz_data:
    st.error("問題データ(questions.json)が見つかりません。")
else:
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0
        st.session_state.score = 0
        st.session_state.show_ans = False

    q = quiz_data[st.session_state.current_idx]
    
    # プログレスバー
    progress = (st.session_state.current_idx + 1) / len(quiz_data)
    st.progress(progress)
    st.write(f"第 {q['chapter']} | 問題 {st.session_state.current_idx + 1} / {len(quiz_data)}")
    
    st.subheader(q['question'])
    
    # 回答選択
    ans = st.radio("選択肢:", q['options'], key=f"radio_{st.session_state.current_idx}")
    
    if st.button("回答をチェック"):
        st.session_state.show_ans = True
        
    if st.session_state.show_ans:
        if ans == q['answer']:
            st.success("✨ 正解！")
        else:
            st.error(f"❌ 不正解（正解: {q['answer']}）")
        
        st.markdown(f"**【シラバス解説】**\n\n{q['explanation']}")
        
        if st.button("次の問題へ ➡️"):
            if st.session_state.current_idx < len(quiz_data) - 1:
                st.session_state.current_idx += 1
                st.session_state.show_ans = False
                st.rerun()
            else:
                st.balloons()
                st.write("🎉 全問題を解き終えました！")