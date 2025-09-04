import os
import re
from dotenv import load_dotenv
import streamlit as st
from fpdf import FPDF
from openai import OpenAI

# ✅ Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# ✅ Get API Key securely
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OpenAI API key not found! Please add it to your `.env` file.")
    st.stop()

# ✅ Initialize OpenAI client
client = OpenAI(api_key=api_key)

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="AI Proposal Generator", page_icon="📝", layout="centered")
st.title("📝 AI Proposal Generator")
st.write("Generate **personalized, client-ready proposals** instantly!")

# -------------------------------
# USER INPUTS
# -------------------------------
client_name = st.text_input("👤 Client Name")
service = st.text_input("💼 Service (e.g., Cybersecurity, Web Development, SEO, etc.)")
budget = st.number_input("💰 Budget ($)", min_value=0)
contact_name = st.text_input("📌 Your Name / Company Name")
contact_email = st.text_input("📧 Your Email")
contact_phone = st.text_input("📞 Your Phone Number")
template = st.selectbox("🎨 Proposal Style", ["Formal", "Creative"])

# -------------------------------
# CLEAN PROPOSAL TEXT FUNCTION
# -------------------------------
def clean_proposal_text(text):
    # Remove markdown ** and *
    text = re.sub(r"\*+", "", text)
    # Remove extra square brackets like [Your Name]
    text = re.sub(r"\[.*?\]", "", text)
    return text.strip()

# -------------------------------
# GENERATE PROPOSAL
# -------------------------------
if st.button("🚀 Generate Proposal"):
    if not client_name or not service or budget <= 0 or not contact_name:
        st.warning("⚠️ Please fill all required fields before generating a proposal.")
    else:
        with st.spinner("⏳ Generating your personalized proposal..."):
            try:
                # Personalized prompt for GPT
                prompt = (
                    f"Create a professional business proposal from '{contact_name}' to '{client_name}'. "
                    f"The proposal should offer '{service}' services for a budget of ${budget}. "
                    "Make it clear that this proposal is from the provider (us) to the client (them). "
                    "Include sections: Cover Greeting, Overview, Service Highlights, Pricing, Why Choose Us, and Contact Info. "
                    "Make it polite, structured, client-focused, and at least 1.5 pages long. "
                    "Avoid placeholders like [Your Name] or [Contact Info]."
                )

                # OpenAI API Call
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                proposal_text = clean_proposal_text(response.choices[0].message.content)

                # -------------------------------
                # PDF GENERATION
                # -------------------------------
                pdf = FPDF()
                pdf.add_page()

                # Set proper margins
                pdf.set_left_margin(20)
                pdf.set_right_margin(20)
                pdf.set_top_margin(15)

                # Load Unicode font
                font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
                if not os.path.exists(font_path):
                    st.error("⚠️ Missing DejaVuSans.ttf! Please place it in a `fonts` folder next to proposal_app.py.")
                    st.stop()

                pdf.add_font("DejaVu", "", font_path, uni=True)
                pdf.set_font("DejaVu", size=14)

                # Title
                pdf.cell(0, 10, "Business Proposal", ln=True, align="C")
                pdf.ln(10)

                # Proposal content with justification
                pdf.set_font("DejaVu", size=12)
                pdf.multi_cell(0, 8, proposal_text, align="J")
                pdf.ln(5)

                # Contact Info Footer
                pdf.set_font("DejaVu", size=12)
                pdf.multi_cell(
                    0, 8,
                    f"---\nPrepared by: {contact_name}\nEmail: {contact_email}\nPhone: {contact_phone}",
                    align="L"
                )

                # Save PDF
                pdf_path = os.path.join(os.getcwd(), "proposal.pdf")
                pdf.output(pdf_path)

                # -------------------------------
                # DISPLAY PROPOSAL + DOWNLOAD
                # -------------------------------
                st.subheader("📄 Generated Proposal")
                st.write(proposal_text)

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇ Download Proposal (PDF)",
                        data=f.read(),
                        file_name="proposal.pdf",
                        mime="application/pdf"
                    )

                # -------------------------------
                # SHARE BUTTON
                # -------------------------------
                st.link_button(
                    "🔗 Share Proposal",
                    f"https://x.com/intent/tweet?text=Check%20out%20my%20personalized%20proposal%20for%20{client_name}!%20Try%20this%20app%20too!"
                )

                # -------------------------------
                # PREMIUM ACCESS (OPTIONAL)
                # -------------------------------
                email = st.text_input("💌 Enter your email for Unlimited Access ($19/mo)")
                if email:
                    st.success("✅ Thanks! We'll contact you about premium access.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")
