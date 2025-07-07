import streamlit as st
import random
import os

# ─── Page Setup ─────────────────────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")
CARD_FOLDER = "card_images"

# Load 21 PNGs (no jokers) from card_images/
all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# ─── Trick Logic ────────────────────────────────────────────────
def deal_into_piles(deck):
    piles = [[], [], []]
    for i, card in enumerate(deck):
        piles[i % 3].append(card)
    return piles

def gather_piles(piles, chosen_idx):
    order = [0, 1, 2]
    order.remove(chosen_idx)
    return piles[order[0]] + piles[chosen_idx] + piles[order[1]]

def reset_game():
    st.session_state.step = 0
    st.session_state.round = 1
    st.session_state.deck = random.sample(all_cards, 21)

# ─── Initialize State ──────────────────────────────────────────
if "step" not in st.session_state:
    reset_game()

# ─── UI Flow ───────────────────────────────────────────────────
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1

elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    cols = st.columns(7)
    for idx, card in enumerate(st.session_state.deck):
        with cols[idx % 7]:
            st.image(f"{CARD_FOLDER}/{card}", width=80)
    if st.button("I've chosen my card!"):
        st.session_state.step = 2

elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Scroll down, find the pile with your card, then tap its button.")

    piles = deal_into_piles(st.session_state.deck)
    for pile_idx, pile in enumerate(piles):
        st.subheader(f"Pile {pile_idx+1}")
        cols = st.columns(7)
        for i, c in enumerate(pile):
            with cols[i % 7]:
                st.image(f"{CARD_FOLDER}/{c}", width=80)

        # One-click per pile
        if st.button(f"Select Pile {pile_idx+1}", key=f"r{st.session_state.round}_p{pile_idx}"):
            st.session_state.deck = gather_piles(piles, pile_idx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3

elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    chosen = st.session_state.deck[10]  # 11th card
    st.image(f"{CARD_FOLDER}/{chosen}", width=200, caption=chosen)
    if st.button("🔁 Play Again"):
        reset_game()
