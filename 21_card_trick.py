import streamlit as st
import random
import os
import base64

# ─── FORCE LIGHT MODE ──────────────────────────────────────────
st.markdown(
    """
    <style>
      /* App background & text */
      html, body, .stApp, .css-18e3th9, .css-1outpf7 {
        background-color: #ffffff !important;
        color: #000000 !important;
      }
      /* Headers and containers */
      .css-ffhzg2, .css-1v0mbdj, .css-1lcbmhc {
        background-color: #ffffff !important;
        color: #000000 !important;
      }
      /* Buttons */
      .stButton>button {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Mobile CSS for card sizing ─────────────────────────────────
st.markdown(
    """
    <style>
      img {
        width: 10vw !important;
        height: auto !important;
        margin: 0 1px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Page Config & Card Folder ─────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")
CARD_FOLDER = "card_images"

# ─── Load card filenames ────────────────────────────────────────
all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# ─── Trick Logic ────────────────────────────────────────────────
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

# ─── Initialize State ──────────────────────────────────────────
if "step" not in st.session_state:
    reset_game()

# ─── Helper: render a row of 7 cards as Base64 data URIs ───────
def render_card_row_base64(cards):
    html = '<div style="display:flex; justify-content:center; margin:4px 0;">'
    for fn in cards:
        path = os.path.join(CARD_FOLDER, fn)
        b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")
        html += (
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width:10vw; height:auto; margin:0" />'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ─── UI Flow ───────────────────────────────────────────────────

# STEP 0: Welcome screen
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1

# STEP 1: Show all 21 cards in 3 rows of 7
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t tap—just keep it in your mind.")
    deck = st.session_state.deck
    render_card_row_base64(deck[0:7])
    render_card_row_base64(deck[7:14])
    render_card_row_base64(deck[14:21])
    if st.button("I've chosen my card!"):
        st.session_state.step = 2

# STEP 2: Three rounds of deal & gather
elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Tap the button under the row (pile) that contains your card.")
    piles = deal_into_piles(st.session_state.deck)
    for idx, pile in enumerate(piles):
        st.subheader(f"Pile {idx+1}")
        render_card_row_base64(pile)
        if st.button(f"Select Pile {idx+1}", key=f"r{st.session_state.round}_p{idx}"):
            st.session_state.deck = gather_piles(piles, idx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    chosen = st.session_state.deck[10]  # index 10 = 11th card
    st.image(os.path.join(CARD_FOLDER, chosen), width=200, caption=chosen)
    if st.button("🔁 Play Again"):
        reset_game()
