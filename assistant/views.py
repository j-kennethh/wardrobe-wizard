from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from closet.models import ClothingItem
from django.conf import settings
from openai import OpenAI

# Create your views here.
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def ai_assistant(request):
    reccomended_items = []

    if request.method == "POST":
        prompt = request.POST.get("prompt")
        tags = list(request.user.clothingitem_set.values_list("tags__name", flat=True).distinct())
        tag_string = ", ".join(tags)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fashion assistant. Suggest suitable clothing tags based on the user's wardrobe and their occasion."},
                {"role": "user", "content": f"My tags: {tag_string}. Prompt: {prompt}"}
            ]
        )

        ai_reply = response["choices"][0]["message"]["content"]
        reccomended_tags = [tag.strip().lower() for tag in ai_reply.split(',')]

        reccomended_items = ClothingItem.objects.filter(
            user=request.user,
            tags__name__in=reccomended_tags
        ).distinct()

    return render(request, "assistant/ai_assistant.html", {"reccomended_items": reccomended_items})
