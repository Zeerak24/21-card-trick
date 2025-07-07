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
    other_piles = [piles[i] for i in range(3) if i != chosen_idx]
    # The chosen pile always goes in the middle
    gathered_deck = other_piles[0] + piles[chosen_idx] + other_piles[1]

    # Debugging prints to console (not in Streamlit app)
    print(f"\n--- After Gathering (Round {st.session_state.round -1}) ---")
    print(f"Chosen Pile Index: {chosen_idx}") # Changed from pile_idx to chosen_idx
    print(f"Gathered Deck (first 11 cards): {gathered_deck[:11]}")
    return gathered_deck

def reset_game():
    """Initialize or reset all session state for a fresh game."""
    st.session_state.step = 0
    st.session_state.round = 1
    st.session_state.deck = random.sample(all_cards, 21)
    st.session_state.chosen_pile = None # Initialize chosen_pile
    # Debugging print
    print(f"\n--- DEBUG: GAME RESET - NEW DECK. First 5 cards: {st.session_state.deck[:5]} ---")

# --- MODIFIED: display_piles_with_buttons for Responsiveness and State Handling ---
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
            card_cols = st.columns(7)
            for i, card in enumerate(pile):
                with card_cols[i % 7]:
                    st.image(f"{CARD_FOLDER}/{card}", width=60) # Smaller width for individual cards

            st.markdown("---") # Separator between cards and button for clarity
            if st.button(f"Select Pile {idx + 1}", key=f"select_pile_{idx}_{st.session_state.round}"):
                st.session_state.chosen_pile = idx # Store the chosen pile index
                st.session_state.round += 1       # Increment round
                st.rerun() # Re-run the script immediately to process selection

        # Add some vertical space between stacked piles
        st.markdown("<br>", unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────
if "step" not in st.session_state:
    reset_game()


# ─── UI Flow ─────────────────────────────────────────────────

# STEP 0: Welcome & Start
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 cards below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1
        st.rerun()

# STEP 1: Show all 21 cards for silent selection
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t click it—just remember it.")
    cols = st.columns(7)
    for idx, card in enumerate(st.session_state.deck):
        with cols[idx % 7]:
            st.image(f"{CARD_FOLDER}/{card}", width=80)
    if st.button("I've chosen my card!"):
        st.session_state.step = 2
        st.rerun()

# STEP 2: Up to 3 rounds of deal & gather
elif st.session_state.step == 2:
    if st.session_state.round <= 3: # Ensure we are in a valid round
        st.title(f"Round {st.session_state.round}: Which pile has your card?")
        st.write("Click the button under the pile that contains your card.")

        # Process the chosen pile from the previous run, IF one was chosen
        if st.session_state.chosen_pile is not None:
            # Re-create the piles from the deck *as it was displayed to the user* before they clicked.
            # This is crucial for `gather_piles` to work on the correct set of piles.
            piles_from_previous_render = deal_into_piles(st.session_state.deck)
            st.session_state.deck = gather_piles(piles_from_previous_render, st.session_state.chosen_pile)
            st.session_state.chosen_pile = None # Reset chosen_pile for the next round

        # Now, deal the (potentially newly gathered) deck for the current round's display.
        if st.session_state.deck:
            print(f"\n--- Round {st.session_state.round}: Deck for Dealing ---")
            print(f"Deck (first 11 cards): {st.session_state.deck[:11]}")
            current_piles_for_display = deal_into_piles(st.session_state.deck)
            display_piles_with_buttons(current_piles_for_display)
        else:
            st.error("Internal error: Deck state invalid during rounds. Resetting game.")
            reset_game()
            st.rerun()
    else: # After Round 3 is complete, move to the reveal step
        st.session_state.step = 3
        st.rerun()


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
        st.rerun()
