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
        /* Default for cards in row context (like in render_card_row_base64) */
        width: 13vw; /* Slightly larger for clarity on some phones, adjust if needed */
        height: auto;
        margin: 0 1px;
      }
      /* Override for the final revealed card if necessary */
      .stImage > img {
          max-width: 200px; /* Max size for the single revealed card */
          width: auto !important; /* Allow the single image to scale up */
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

# Error handling for card images (important for deployment)
if not os.path.exists(CARD_FOLDER):
    st.error(f"Error: The '{CARD_FOLDER}' folder does not exist. Please create it and add your card images (.png files).")
    st.stop()
if len(all_cards) < 21:
    st.error(f"Error: Not enough card images in '{CARD_FOLDER}'. You need at least 21 unique card images (excluding jokers). Found: {len(all_cards)}")
    st.stop()


# ─── Trick Logic ────────────────────────────────────────────────
def deal_into_piles(deck):
    """Round-robin deal 21 cards into 3 piles of 7 each."""
    piles = [[], [], []]
    for i, c in enumerate(deck):
        piles[i % 3].append(c)
    return piles

def gather_piles(piles, chosen_idx):
    """Stack piles so the chosen pile is in the middle."""
    # Corrected original logic: Find the other two piles by their indices and order them
    order = [0, 1, 2]
    order.remove(chosen_idx)
    # The chosen pile is always placed in the middle
    return piles[order[0]] + piles[chosen_idx] + piles[order[1]]


def reset_game():
    """Initialize or reset all session state for a fresh game."""
    st.session_state.step  = 0
    st.session_state.round = 1
    # Only clear the deck state. Actual randomization happens in STEP 0 or 1.
    if 'deck' in st.session_state:
        del st.session_state.deck
    # Ensure any temporary state variables are cleaned up for a fresh game
    if 'chosen_pile_index_for_gather' in st.session_state:
        del st.session_state.chosen_pile_index_for_gather
    # Debugging print
    print(f"\n--- DEBUG: GAME RESET ---")


# --- DEFINITION OF display_responsive_piles_with_buttons ---
# This function MUST be defined before it is called in the UI Flow.
def display_responsive_piles_with_buttons(piles):
    """
    Displays the three piles with selection buttons below them,
    optimized for vertical stacking on smaller screens, using base64 rendering.
    """
    for idx, pile in enumerate(piles):
        # Wrap each pile in a container for visual grouping and separation
        # This container will stack vertically by default on narrow screens
        with st.container(border=True):
            st.subheader(f"Pile {idx + 1}") # Changed to subheader for consistency with render_card_row_base64
            render_card_row_base64(pile) # Use the Base64 rendering helper
            st.markdown("---") # Separator between cards and button for clarity
            # IMPORTANT: The button click must store the pile index and trigger a rerun
            if st.button(f"Select Pile {idx + 1}", key=f"select_pile_{idx}_{st.session_state.round}"):
                st.session_state.chosen_pile_index_for_gather = idx # Store the chosen pile index
                st.session_state.round += 1                         # Increment round
                st.rerun() # Re-run the script immediately to process selection

        # Add some vertical space between stacked piles for better readability on mobile
        st.markdown("<br>", unsafe_allow_html=True)


# ─── Initialize State ──────────────────────────────────────────
# This ensures a clean state on first load or after a full app refresh
if "step" not in st.session_state:
    reset_game()

# Ensure chosen_pile_index_for_gather is initialized
if 'chosen_pile_index_for_gather' not in st.session_state:
    st.session_state.chosen_pile_index_for_gather = None


# ─── Helper: render a row of 7 cards as Base64 data URIs ───────
def render_card_row_base64(cards):
    """Renders a horizontal row of cards using Base64 data URIs for direct HTML embedding."""
    html = '<div style="display:flex; justify-content:center; flex-wrap: wrap; margin:4px 0;">'
    for fn in cards:
        path = os.path.join(CARD_FOLDER, fn)
        # Ensure the file exists before trying to read it
        if os.path.exists(path):
            try:
                b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")
                html += (
                    f'<img src="data:image/png;base64,{b64}" '
                    f'style="width:13vw; height:auto; margin:0 1px; min-width: 50px;" />'
                )
            except Exception as e:
                st.error(f"Error loading image {fn}: {e}")
                html += f'<div style="width:13vw; height:80px; border:1px solid red; display:flex; align-items:center; justify-content:center;">ERR</div>'
        else:
            st.warning(f"Card image not found: {path}")
            html += f'<div style="width:13vw; height:80px; border:1px solid red; display:flex; align-items:center; justify-content:center;">MISSING</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ─── UI Flow ───────────────────────────────────────────────────

# STEP 0: Welcome screen
if st.session_state.step == 0:
    st.title("🃏 21-Card Magic Trick")
    st.write("Silently pick one card in your mind from the 21 shown below.")
    if st.button("✨ Start Trick"):
        st.session_state.step = 1
        st.session_state.deck = random.sample(all_cards, 21) # Randomize deck for initial selection
        st.rerun() # Ensures immediate transition to next step

# STEP 1: Show all 21 cards for silent selection
elif st.session_state.step == 1:
    st.title("Step 1: Remember Your Card")
    st.write("Don’t tap—just keep it in your mind.")
    # Display the deck for initial selection
    deck_to_display = st.session_state.deck # This is the randomized deck from Step 0
    render_card_row_base64(deck_to_display[0:7])
    render_card_row_base64(deck_to_display[7:14])
    render_card_row_base64(deck_to_display[14:21])
    if st.button("I've chosen my card!"):
        st.session_state.step = 2
        random.shuffle(st.session_state.deck) # IMPORTANT: Re-shuffle the SAME 21 cards for Round 1
        st.rerun() # Ensures immediate transition to next step

# STEP 2: Three rounds of deal & gather
elif st.session_state.step == 2:
    # Process the chosen pile from the previous rerun, IF one was chosen
    if st.session_state.chosen_pile_index_for_gather is not None and st.session_state.round <= 3:
        # Re-create the piles from the active_game_deck *as it was displayed to the user* before they clicked.
        # Use st.session_state.deck here as it's the single source of truth for the active game deck
        piles_from_previous_render = deal_into_piles(st.session_state.deck)
        st.session_state.deck = gather_piles(piles_from_previous_render, st.session_state.chosen_pile_index_for_gather)
        st.session_state.chosen_pile_index_for_gather = None # Reset for next selection

    # After processing the previous selection (if any), now display for the current round
    if st.session_state.round <= 3: # Continue with rounds 1, 2, 3
        st.title(f"Round {st.session_state.round} of 3")
        st.write("Tap the button under the row (pile) that contains your card.")

        # Ensure deck is valid before dealing
        if st.session_state.deck:
            print(f"\n--- Round {st.session_state.round}: Deck for Dealing ---")
            print(f"Deck (first 11 cards): {st.session_state.deck[:11]}")
            current_piles_for_display = deal_into_piles(st.session_state.deck)
            display_responsive_piles_with_buttons(current_piles_for_display) # Call the responsive display function
        else:
            st.error("Internal error: Deck state invalid during rounds. Resetting game.")
            reset_game()
            st.rerun()
    else: # After Round 3 is complete, move to the reveal step
        st.session_state.step = 3
        st.rerun()

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    # Use st.session_state.deck for the final reveal
    chosen = st.session_state.deck[10]  # index 10 = 11th card

    st.image(os.path.join(CARD_FOLDER, chosen), width=200, caption=chosen)
    st.balloons() # Added celebration!

    if st.button("🔁 Play Again"):
        reset_game() # Call the reset function
        st.rerun() # Re-run the script to show the welcome screen with a new deck
