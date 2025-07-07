import streamlit as st
import random
import os
import base64

# ─── FORCE LIGHT MODE ──────────────────────────────────────────
st.markdown(
    """
    <style>
      html, body, .stApp, .css-18e3th9, .css-1outpf7 {
        background-color: #ffffff !important;
        color: #000000 !important;
      }
      .css-ffhzg2, .css-1v0mbdj, .css-1lcbmhc {
        background-color: #ffffff !important;
        color: #000000 !important;
      }
      .stButton>button {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── MOBILE CSS FOR CARD SIZING ─────────────────────────────────
st.markdown(
    """
    <style>
      img {
        width: 13vw !important;
        height: auto !important;
        margin: 0 1px !important;
      }
      .stImage > img {
        max-width: 200px;
        width: auto !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── PAGE CONFIG & LOAD IMAGES ─────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")
CARD_FOLDER = "card_images"

# Gather all non-joker PNGs
all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# Error if folder missing or too few cards
if not os.path.exists(CARD_FOLDER):
    st.error(f"Error: '{CARD_FOLDER}' folder not found. Add 21 PNGs here.")
    st.stop()
if len(all_cards) < 21:
    st.error(f"Error: Need 21 card images, found {len(all_cards)}.")
    st.stop()


# ─── TRICK LOGIC ────────────────────────────────────────────────
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
    # Pick a fresh 21 from the full 52
    st.session_state.deck  = random.sample(all_cards, 21)

# Initialize on first load
if "step" not in st.session_state:
    reset_game()


# ─── HELPER TO RENDER A ROW OF 7 CARDS ─────────────────────────
def render_card_row_base64(cards):
    html = '<div style="display:flex; justify-content:center; margin:4px 0;">'
    for fn in cards:
        path = os.path.join(CARD_FOLDER, fn)
        data = base64.b64encode(open(path, "rb").read()).decode("utf-8")
        html += (
            f'<img src="data:image/png;base64,{data}" '
            f'style="width:13vw; height:auto; margin:0 1px;" />'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─── UI FLOW ───────────────────────────────────────────────────

# STEP 0: Welcome
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1
        st.rerun()

# STEP 1: Show all 21 cards; once chosen, shuffle that same deck
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t tap—just keep it in your mind.")
    deck = st.session_state.deck
    render_card_row_base64(deck[0:7])
    render_card_row_base64(deck[7:14])
    render_card_row_base64(deck[14:21])
    if st.button("I've chosen my card!"):
        # Shuffle *only* these 21 cards for round 1
        random.shuffle(st.session_state.deck)
        st.session_state.step = 2
        st.rerun()

# STEP 2: Three deal-gather rounds on that same deck
elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Tap the button under the row containing your card.")
    piles = deal_into_piles(st.session_state.deck)
    for idx, pile in enumerate(piles):
        st.subheader(f"Pile {idx+1}")
        render_card_row_base64(pile)
        if st.button(f"Select Pile {idx+1}", key=f"r{st.session_state.round}_p{idx}"):
            st.session_state.deck = gather_piles(piles, idx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3
            st.rerun()

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    chosen = st.session_state.deck[10]  # 11th card
    st.image(os.path.join(CARD_FOLDER, chosen), width=200, caption=chosen)
    st.balloons()
    if st.button("🔁 Play Again"):
        reset_game()
        st.rerun()

# ─── AUTHOR CREDIT ─────────────────────────────────────────────
st.markdown("---")
st.caption("Made by Zeerak Shah")
