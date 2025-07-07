import streamlit as st
import random
import os

# ─── Light-mode CSS ──────────────────────────────────────────
st.markdown(
    """
    <style>
      /* App background */
      .stApp {
        background-color: #ffffff;
      }
      /* Main content container */
      .css-18e3th9 {
        background-color: #ffffff;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Page config ─────────────────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")

CARD_FOLDER = "card_images"
all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# ─── Trick logic ──────────────────────────────────────────────
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

# ─── Initialize state ─────────────────────────────────────────
if "step" not in st.session_state:
    reset_game()

# ─── UI Flow ──────────────────────────────────────────────────

# STEP 0: Welcome
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1

# STEP 1: Show all 21 cards for silent selection
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t tap the card—just remember it.")
    piles = deal_into_piles(st.session_state.deck)
    # Show each pile (7 cards) stacked vertically
    for i, pile in enumerate(piles):
        st.subheader(f"Row {i+1}: 7 cards")
        cols = st.columns(7)
        for idx, card in enumerate(pile):
            with cols[idx]:
                st.image(f"{CARD_FOLDER}/{card}", width=80)
    if st.button("I've chosen my card!"):
        st.session_state.step = 2

# STEP 2: 3 rounds of vertical pile selection
elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Scroll down, find the pile with your card, then tap its button.")
    piles = deal_into_piles(st.session_state.deck)

    # Stack piles vertically
    for pile_idx, pile in enumerate(piles):
        st.subheader(f"Pile {pile_idx+1}")
        # Show cards in a single horizontal row of 7
        cols = st.columns(7)
        for idx, c in enumerate(pile):
            with cols[idx]:
                st.image(f"{CARD_FOLDER}/{c}", width=80)
        # One-click selection
        if st.button(f"Select Pile {pile_idx+1}", key=f"r{st.session_state.round}_p{pile_idx}"):
            st.session_state.deck = gather_piles(piles, pile_idx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    chosen = st.session_state.deck[10]  # index 10 = 11th card
    st.image(f"{CARD_FOLDER}/{chosen}", width=200, caption=chosen)
    if st.button("🔁 Play Again"):
        reset_game()
