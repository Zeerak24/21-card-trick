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

# ─── MOBILE CSS FOR CARD SIZING ─────────────────────────────────
st.markdown(
    """
    <style>
      img {
        width: 13vw !important;
        height: auto !important;
        margin: 0 1px !important;
        min-width: 50px;
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
st.set_page_config(page_title="The Mind-Reading Deck", layout="centered")
CARD_FOLDER = "card_images"

all_cards = [
    f for f in os.listdir(CARD_FOLDER)
    if f.lower().endswith(".png") and "joker" not in f.lower()
]

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
    st.session_state.deck  = random.sample(all_cards, 21)
    st.session_state.guessed_pile_idx = None
    st.session_state.show_guess_phase = True
    st.session_state.last_guess_was_no = False
    st.session_state.wrong_guess_history = [] # Stores indices of previously "wrongly" guessed piles

# Ensure initial state is set
if "step" not in st.session_state:
    reset_game()

# Initialize new state variables if they don't exist (for app reloads/first run)
if "guessed_pile_idx" not in st.session_state:
    st.session_state.guessed_pile_idx = None
if "show_guess_phase" not in st.session_state:
    st.session_state.show_guess_phase = True
if "last_guess_was_no" not in st.session_state:
    st.session_state.last_guess_was_no = False
if "wrong_guess_history" not in st.session_state:
    st.session_state.wrong_guess_history = []


# ─── HELPER TO RENDER A ROW OF 7 CARDS ─────────────────────────
def render_card_row_base64(cards):
    html = '<div style="display:flex; justify-content:center; margin:4px 0;">'
    for fn in cards:
        path = os.path.join(CARD_FOLDER, fn)
        try:
            b64 = base64.b64encode(open(path, "rb").read()).decode("utf-8")
            html += (
                f'<img src="data:image/png;base64,{b64}" '
                f'style="width:13vw; height:auto; margin:0 1px; min-width: 50px;" />'
            )
        except FileNotFoundError:
            st.error(f"Error: Card image not found at {path}. Please check your 'card_images' folder.")
            html += f'<div style="width:13vw; height:80px; border:1px solid red; display:flex; align-items:center; justify-content:center;">Missing</div>'
        except Exception as e:
            st.error(f"Error processing image {fn}: {e}")
            html += f'<div style="width:13vw; height:80px; border:1px solid red; display:flex; align-items:center; justify-content:center;">Error</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ─── UI FLOW ───────────────────────────────────────────────────

# STEP 0: Welcome screen
if st.session_state.step == 0:
    st.caption("Made by Zeerak Shah")
    st.title("🃏 The Mystic Card Revelation")
    st.write("Prepare to witness a phenomenon. This deck will reveal your innermost thoughts.")
    if st.button("✨ Begin the Revelation!"):
        st.session_state.step = 1
        st.rerun()

# STEP 1: Show all 21 cards; once chosen, shuffle that same deck
elif st.session_state.step == 1:
    st.caption("Made by Zeerak Shah")
    st.title("✨ **The Connection Begins: Choose Your Destiny Card** ✨")
    st.write("Gaze upon these ancient symbols. Without a word, let one card speak to your soul. This is your secret. This is your power. Let me guess your card in only 3 rounds")
    deck = st.session_state.deck
    render_card_row_base64(deck[0:7])
    render_card_row_base64(deck[7:14])
    render_card_row_base64(deck[14:21])
    if st.button("My secret card is chosen!"):
        random.shuffle(st.session_state.deck)
        st.session_state.step = 2
        # Initial guess setup for Round 1: make a "wrong" guess
        # Pick 0 or 2 for the first wrong guess, avoiding 1 (the always-correct middle pile)
        st.session_state.guessed_pile_idx = random.choice([0, 2])
        st.session_state.wrong_guess_history = [st.session_state.guessed_pile_idx] # Store this initial wrong guess
        st.session_state.show_guess_phase = True
        st.session_state.last_guess_was_no = False
        st.rerun()

# STEP 2: Three deal-gather rounds on that same deck
elif st.session_state.step == 2:
    st.caption("Made by Zeerak Shah")
    st.title(f"Round {st.session_state.round} of 3: The Gathering of Secrets")
    
    piles = deal_into_piles(st.session_state.deck)

    # --- Pre-pile messages based on round and last guess ---
    if st.session_state.show_guess_phase: # Message before the guess attempt
        if st.session_state.round == 1:
            st.write("I'm focusing... the energies are a bit murky today... Let's see if my intuition can cut through the fog...")
        elif st.session_state.round == 2:
            st.write("The energies are shifting again... still a slight interference. Your thoughts are well-shielded! But I press on!")
        elif st.session_state.round == 3:
            st.write("This is it. The final, most crucial round. The energies of the cards are aligning perfectly. I feel it now, a profound connection...")
            st.write("At this point, if I don't reveal your exact card, you have my full permission to *slap me senseless!* (But you won't need to.)")
    elif st.session_state.last_guess_was_no: # Message after a 'No' and before player selection
        st.write("Aha! A clever twist! My apologies, the energy shifted. The cards are testing me, and perhaps you. Now, *you* must guide your card. Which pile truly holds your secret?")
        st.session_state.last_guess_was_no = False # Reset after displaying

    for idx, pile in enumerate(piles):
        st.subheader(f"Pile {idx+1}")
        render_card_row_base64(pile)

        # --- Guess Phase Logic ---
        if st.session_state.show_guess_phase and st.session_state.guessed_pile_idx == idx:
            st.write(f"Is your card in **Pile {idx+1}**?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, that's it!", key=f"r{st.session_state.round}_guess_yes"):
                    st.session_state.deck = gather_piles(piles, idx) # Gather based on the *guessed* pile
                    st.session_state.round += 1
                    
                    # Prepare for next round's guess based on the "struggling magician" strategy
                    if st.session_state.round <= 2: # For Round 1 and 2, the app's guess is "wrong"
                        # Next "wrong" guess should be the other non-middle pile not yet guessed
                        # If R1 guessed 0, R2 guesses 2. If R1 guessed 2, R2 guesses 0.
                        st.session_state.guessed_pile_idx = 0 if st.session_state.wrong_guess_history[0] == 2 else 2
                        st.session_state.wrong_guess_history.append(st.session_state.guessed_pile_idx)
                    else: # For Round 3, the app's guess is always the correct middle pile
                        st.session_state.guessed_pile_idx = 1 # Middle pile (index 1) is always correct for the final guess
                    
                    st.session_state.show_guess_phase = True # Always start next round with a guess
                    st.session_state.last_guess_was_no = False # Reset this flag
                    
                    if st.session_state.round > 3: # If all 3 rounds are done, move to reveal
                        st.session_state.step = 3
                    st.rerun()
            with col_no:
                if st.button("No, not that one.", key=f"r{st.session_state.round}_guess_no"):
                    st.session_state.show_guess_phase = False # End guess for this round, move to player selection
                    st.session_state.last_guess_was_no = True # Set flag to display "Oh, my apologies!" message
                    st.rerun()
        
        # --- Player Selection Phase (appears if guess was 'No' or if guess phase is currently off) ---
        elif not st.session_state.show_guess_phase: 
             if st.button(f"Select Pile {idx+1}", key=f"r{st.session_state.round}_p{idx}"):
                st.session_state.deck = gather_piles(piles, idx) # Gather based on player's chosen pile
                st.session_state.round += 1
                
                # Prepare for next round's guess based on the "struggling magician" strategy
                if st.session_state.round <= 2: # For Round 1 and 2, the app's guess is "wrong"
                    st.session_state.guessed_pile_idx = 0 if st.session_state.wrong_guess_history[0] == 2 else 2
                    if len(st.session_state.wrong_guess_history) < 2: # Only add if it's a new wrong guess
                        st.session_state.wrong_guess_history.append(st.session_state.guessed_pile_idx)
                else: # For Round 3, the app's guess is always the correct middle pile
                    st.session_state.guessed_pile_idx = 1 # Middle pile (index 1) is always correct for the final guess
                
                st.session_state.show_guess_phase = True # Always start next round with a guess
                st.session_state.last_guess_was_no = False # Reset this flag
                
                if st.session_state.round > 3: # If all 3 rounds are done, move to reveal
                    st.session_state.step = 3
                st.rerun()

# STEP 3: Reveal the 11th card
elif st.session_state.step == 3:
    st.caption("Made by Zeerak Shah")
    st.title("🔮 **The Unveiling!** 🔮")
    st.write("The magic is complete. After our shared journey through the cards, your chosen card has risen to its destined place. Prepare for the revelation of your deepest thoughts...")
    chosen = st.session_state.deck[10] # The 11th card (index 10) is always the chosen card
    st.image(os.path.join(CARD_FOLDER, chosen), width=200, caption="Behold! Your secret card, revealed by the ancient art of the cards prophecy!")
    st.balloons()
    if st.button("Witness the Magic Again!"):
        reset_game()
        st.rerun()
