import google.generativeai as genai
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from closet.models import ClothingItem


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

@login_required
def ai_assistant(request):
    response_text = None
    reccomended_items = []

    # Get items from user's closet
    user_items = ClothingItem.objects.filter(user=request.user)
    item_names = user_items.values_list("title", flat=True).distinct()

    if request.method == "POST":
        user_prompt = request.POST.get("prompt", "")

        # Create detailed prompt for Gemini
        full_prompt = {
            f"You are a fashion assistant. This is the user's request.\n"
            f"{user_prompt}\n\n"
            f"Here are the user's clothes: {', '.join(item_names)}.\n"
            f"From this list, choose the most suitable items for the occasion. Respond only with the chosen items separated by commas."
        }

        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(full_prompt)
            response_text = response.text.strip()

            # Parse through the response to get the items
            chosen_items = [item.strip() for item in response_text.split(',') if item.strip()]

            # Filter clothing items by chosen items
            reccomended_items = user_items.filter(title__in=chosen_items)

        except Exception as e:
            response_text = f"Error: {e}"

    return render(request, "assistant/ai_assistant.html", {"response_text": response_text, "reccomended_items": reccomended_items})
