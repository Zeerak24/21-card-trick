import streamlit as st
import random
import os

# ─── Mobile-friendly CSS ───────────────────────────────────────
st.markdown(
    """
    <style>
      /* make every card image exactly 1/7 of viewport width */
      img {
        max-width: calc(100vw / 7) !important;
        height: auto !important;
      }
      /* white background for mobile */
      .stApp, .css-18e3th9 {
        background-color: #ffffff;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Page config & images ─────────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")
CARD_FOLDER = "card_images"
all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# ─── Trick logic ───────────────────────────────────────────────
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
    st.session_state.step = 0
    st.session_state.round = 1
    st.session_state.deck = random.sample(all_cards, 21)

if "step" not in st.session_state:
    reset_game()

# ─── UI Flow ──────────────────────────────────────────────────

# STEP 0: Welcome
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently choose one card in your mind from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1

# STEP 1: Show all 21 as 3 rows of 7
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t tap—just remember it in your mind.")
    for row in range(3):
        cols = st.columns(7)
        for i, card in enumerate(st.session_state.deck[row*7:(row+1)*7]):
            with cols[i]:
                st.image(f"{CARD_FOLDER}/{card}")
    if st.button("I've chosen my card!"):
        st.session_state.step = 2

# STEP 2: 3 rounds, each time show 3 piles as rows of 7
elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Tap the button under the row (pile) that contains your card.")
    piles = deal_into_piles(st.session_state.deck)

    # display each pile as one horizontal row of 7
    for pidx, pile in enumerate(piles):
        st.subheader(f"Pile {pidx+1}")
        cols = st.columns(7)
        for i, card in enumerate(pile):
            with cols[i]:
                st.image(f"{CARD_FOLDER}/{card}")
        if st.button(f"Select Pile {pidx+1}", key=f"r{st.session_state.round}_p{pidx}"):
            st.session_state.deck = gather_piles(piles, pidx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Magic Reveal!")
    card = st.session_state.deck[10]  # index 10 = 11th
    st.image(f"{CARD_FOLDER}/{card}", width=200, caption=card)
    if st.button("🔁 Play Again"):
        reset_game()
