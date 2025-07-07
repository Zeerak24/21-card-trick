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
        /*
        The original width: 10vw !important; was fine for the general layout,
        but for the 21 initial cards, we need to ensure they don't break lines awkwardly.
        For pile display, 10vw is likely good.
        */
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
    order = [0, 1, 2]
    order.remove(chosen_idx)
    # unchosen, chosen, other-unchosen
    return piles[order[0]] + piles[chosen_idx] + piles[order[1]]

def reset_game():
    """Initialize or reset all session state for a fresh game."""
    st.session_state.step  = 0
    st.session_state.round = 1
    st.session_state.deck  = random.sample(all_cards, 21)
    # Ensure any temporary state variables are cleaned up for a fresh game
    if 'processing_selection' in st.session_state:
        del st.session_state.processing_selection


# ─── Initialize State ──────────────────────────────────────────
# This ensures a clean state on first load or after a full app refresh
if "step" not in st.session_state:
    reset_game()

# This is a temporary flag to manage the double-click issue
# We need to ensure it's initialized
if 'processing_selection' not in st.session_state:
    st.session_state.processing_selection = False


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
                    f'style="width:13vw; height:auto; margin:0 1px; min-width: 50px;" />' # Added min-width for very small screens
                )
            except Exception as e:
                st.error(f"Error loading image {fn}: {e}")
                # Fallback or placeholder if image fails to load
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
        st.rerun() # Added rerun: Immediately go to Step 1

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
        st.rerun() # Added rerun: Immediately go to Step 2

# STEP 2: Three rounds of deal & gather
elif st.session_state.step == 2:
    st.title(f"Round {st.session_state.round} of 3")
    st.write("Tap the button under the row (pile) that contains your card.")

    piles = deal_into_piles(st.session_state.deck)

    # Use a temporary state variable to manage the selection and avoid re-processing
    # if st.session_state.processing_selection == False: # This check can sometimes interfere with quick reruns
    for idx, pile in enumerate(piles):
        st.subheader(f"Pile {idx+1}")
        render_card_row_base64(pile) # Uses the Base64 rendering for piles
        if st.button(f"Select Pile {idx+1}", key=f"r{st.session_state.round}_p{idx}"):
            # When a button is clicked, immediately update state and rerun
            # The logic to update the deck and round progression needs to happen *before* the next render
            st.session_state.deck = gather_piles(piles, idx)
            st.session_state.round += 1
            if st.session_state.round > 3:
                st.session_state.step = 3
            st.rerun() # Added rerun: Crucial for immediate processing and redraw

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.title("🎉 The Reveal!")
    chosen = st.session_state.deck[10]  # index 10 = 11th card

    # Render the final chosen card using standard st.image as it's a single image
    # The CSS for img { width: 10vw !important; } might make this too small,
    # so we override it with a fixed width here.
    st.image(os.path.join(CARD_FOLDER, chosen), width=200, caption=chosen)
    st.balloons() # Added celebration!

    if st.button("🔁 Play Again"):
        reset_game()
        st.rerun() # Added rerun: Immediately go back to Step 0
