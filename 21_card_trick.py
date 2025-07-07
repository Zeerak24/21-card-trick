import streamlit as st
import random
import os

# ─── Configuration ────────────────────────────────────────────
st.set_page_config(page_title="21-Card Magic Trick", layout="centered")
CARD_FOLDER = "card_images"

# Load all non-joker PNGs from card_images/
all_cards = [
    f
    for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

# Error handling for card images
if not os.path.exists(CARD_FOLDER):
    st.error(f"Error: The '{CARD_FOLDER}' folder does not exist. Please create it and add your card images (.png files).")
    st.stop()
if len(all_cards) < 21:
    st.error(f"Error: Not enough card images in '{CARD_FOLDER}'. You need at least 21 unique card images (excluding jokers). Found: {len(all_cards)}")
    st.stop()

# ─── Core Trick Logic ─────────────────────────────────────────

def deal_into_piles(deck):
    """Round-robin deal 21 cards into 3 piles of 7 each."""
    piles = [[], [], []]
    for i, card in enumerate(deck):
        piles[i % 3].append(card)
    return piles

def gather_piles(piles, chosen_idx):
    """Stack piles so the chosen pile is in the middle."""
    order = [0, 1, 2]
    order.remove(chosen_idx)
    # unchosen, chosen, other-unchosen
    return piles[order[0]] + piles[chosen_idx] + piles[order[1]]

def reset_game():
    """Initialize or reset all session state for a fresh game."""
    st.session_state.step = 0
    st.session_state.round = 1
    st.session_state.deck = random.sample(all_cards, 21)
    # Debugging print
    print(f"\n--- DEBUG: GAME RESET - NEW DECK. First 5 cards: {st.session_state.deck[:5]} ---")

# --- MODIFIED: display_piles_with_buttons for Responsiveness ---
def display_piles_with_buttons(piles):
    """
    Displays the three piles with selection buttons below them,
    optimized for vertical stacking on smaller screens.
    """
    for idx, pile in enumerate(piles):
        # Wrap each pile in a container for visual grouping and separation
        with st.container(border=True):
            st.header(f"Pile {idx + 1}")
            
            # Use columns *within* each pile to try and fit cards horizontally
            # If 7 columns are too wide, Streamlit will wrap them automatically.
            card_cols = st.columns(7)
            for i, card in enumerate(pile):
                with card_cols[i % 7]: # Distribute cards across these 7 sub-columns
                    st.image(f"{CARD_FOLDER}/{card}", width=60) # Smaller width for individual cards

            st.markdown("---") # Separator between cards and button for clarity
            if st.button(f"Select Pile {idx + 1}", key=f"round{st.session_state.round}_pile{idx}"):
                # gather immediately
                st.session_state.deck = gather_piles(piles, pile_idx)
                st.session_state.round += 1
                # after 3 gathers, move to reveal
                if st.session_state.round > 3:
                    st.session_state.step = 3
                st.rerun() # Crucial: Re-run immediately after any pile selection
        
        # Add some vertical space between stacked piles
        st.markdown("<br>", unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────
# This block ensures all necessary session state variables are initialized
# or re-initialized based on the current game flow.
if "step" not in st.session_state:
    reset_game() # Call reset_game for initial setup


# ─── UI Flow ─────────────────────────────────────────────────

# STEP 0: Welcome & Start
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 cards below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1
        st.rerun() # Ensure immediate re-run after start button

# STEP 1: Show all 21 cards for silent selection
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t click it—just remember it.")
    cols = st.columns(7)
    for idx, card in enumerate(st.session_state.deck):
        with cols[idx % 7]:
            st.image(f"{CARD_FOLDER}/{card}", width=80) # Adjusted width for better display of 21 cards
    if st.button("I've chosen my card!"):
        st.session_state.step = 2
        st.rerun() # Ensure immediate re-run after selection confirmation

# STEP 2: Up to 3 rounds of deal & gather
elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Click the button under the pile that contains your card.")

    piles = deal_into_piles(st.session_state.deck)

    # Use the responsive display function
    display_piles_with_buttons(piles)

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Magic Reveal!")
    st.write("Your card is...")

    # 11th card is index 10
    if st.session_state.deck and len(st.session_state.deck) > 10:
        card = st.session_state.deck[10]
        st.image(f"{CARD_FOLDER}/{card}", width=200, caption=card)
        st.balloons()
    else:
        st.error("Error: Could not reveal the card. The deck might be in an invalid state. Please play again.")

    if st.button("🔁 Play Again"):
        reset_game()
        st.rerun() # Ensure immediate re-run after Play Again
