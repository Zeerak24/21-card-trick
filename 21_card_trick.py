import streamlit as st
import random
import os
import base64

# ─── Page Setup ────────────────────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")
CARD_FOLDER = "card_images"

# ─── Load filenames ────────────────────────────────────────────
all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# ─── Trick Logic ───────────────────────────────────────────────
def deal_into_piles(deck):
    piles = [[], [], []]
    for i, c in enumerate(deck):
        piles[i % 3].append(c)
    return piles

def gather_piles(piles, chosen_idx):
    order = [0, 1, 2]
    order.remove(chosen_idx)
    return piles[order[0]] + piles[chosen_idx] + piles[order[1]]

def reset_game():
    st.session_state.step  = 0
    st.session_state.round = 1
    st.session_state.deck  = random.sample(all_cards, 21)

# ─── Init State ───────────────────────────────────────────────
if "step" not in st.session_state:
    reset_game()

# ─── Helper: embed a row of 7 cards as Base64 HTML ────────────
def render_card_row_base64(cards):
    html = '<div style="display:flex; justify-content:center; margin:4px 0;">'
    for fn in cards:
        path = os.path.join(CARD_FOLDER, fn)
        data = base64.b64encode(open(path, "rb").read()).decode("utf-8")
        html += (
            f'<img src="data:image/png;base64,{data}" '
            f'style="width:calc(100vw/7); height:auto; margin:0" />'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ─── UI Flow ──────────────────────────────────────────────────
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1

elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t tap—just remember it.")
    deck = st.session_state.deck
    # three rows of 7
    render_card_row_base64(deck[0:7])
    render_card_row_base64(deck[7:14])
    render_card_row_base64(deck[14:21])
    if st.button("I've chosen my card!"):
        st.session_state.step = 2

elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Tap the button under the row containing your card.")
    piles = deal_into_piles(st.session_state.deck)
    # for each pile show its row + a button
    for idx, pile in enumerate(piles):
        st.subheader(f"Pile {idx+1}")
        render_card_row_base64(pile)
        if st.button(f"Select Pile {idx+1}", key=f"r{st.session_state.round}_p{idx}"):
            st.session_state.deck = gather_piles(piles, idx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3

elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    chosen = st.session_state.deck[10]  # 11th card
    img_path = os.path.join(CARD_FOLDER, chosen)
    st.image(img_path, width=200, caption=chosen)
    if st.button("🔁 Play Again"):
        reset_game()
