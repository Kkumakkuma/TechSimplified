"""
TechSimplified Auto Post Generator
Generates SEO-optimized tech guides using OpenAI GPT API
"""

from openai import OpenAI
import datetime
import os
import random
import re

TOPIC_POOLS = {
    "how_to": [
        "How to Speed Up Your Computer in {number} Easy Steps",
        "How to Set Up a VPN on Any Device in {year}",
        "How to Free Up Storage on Your Phone Fast",
        "How to Transfer Files Between Phone and PC Wirelessly",
        "How to Set Up Two-Factor Authentication on Everything",
        "How to Back Up Your Phone Automatically in {year}",
        "How to Screen Record on Any Device",
    ],
    "ai_tools": [
        "Best Free AI Tools You Should Be Using in {year}",
        "{number} AI Productivity Tools That Save Hours Every Week",
        "How to Use AI to Write Emails Faster",
        "Best AI Image Generators Compared {year}",
        "How to Use ChatGPT Like a Pro: {number} Tips",
        "AI Tools for Students: Complete Guide {year}",
        "How to Automate Your Work with AI in {year}",
    ],
    "cybersecurity": [
        "How to Know If Your Password Has Been Hacked",
        "{number} Signs Your Phone Has Been Hacked",
        "Best Password Managers Compared {year}",
        "How to Spot Phishing Emails: {number} Red Flags",
        "How to Protect Your Privacy Online in {year}",
        "Is Public WiFi Safe? What You Need to Know",
        "How to Remove Your Personal Data from the Internet",
    ],
    "software": [
        "Best Free Alternatives to Expensive Software in {year}",
        "Google Sheets Tips and Tricks You Did Not Know",
        "{number} Hidden Features in Windows 11",
        "Best Browser Extensions for Productivity in {year}",
        "How to Use Notion for Beginners: Complete Guide",
        "Excel vs Google Sheets: Which Should You Use in {year}",
        "Best Free Photo Editing Software in {year}",
    ],
    "troubleshooting": [
        "WiFi Keeps Disconnecting? {number} Ways to Fix It",
        "Computer Running Slow? {number} Fixes That Actually Work",
        "How to Fix Bluetooth Not Working on Windows",
        "Phone Battery Draining Fast? {number} Proven Fixes",
        "How to Fix Chrome Using Too Much Memory",
        "Laptop Overheating? {number} Ways to Cool It Down",
        "How to Fix Slow Internet Speed at Home",
    ],
    "gadgets": [
        "Best Budget Laptops Under $500 in {year}",
        "Best Wireless Earbuds Compared {year}",
        "iPhone vs Android: Which Is Better in {year}",
        "Best Smart Home Devices for Beginners in {year}",
        "Best Monitors for Working from Home {year}",
        "Mechanical vs Membrane Keyboard: Which to Choose",
        "Best External Hard Drives and SSDs in {year}",
    ],
}

SYSTEM_PROMPT = """You are an expert tech writer for a blog called TechSimplified.
Write SEO-optimized, informative, and easy-to-follow tech guides.

Rules:
- Write in a friendly, clear tone that anyone can understand
- No jargon without explanation
- Use short paragraphs (2-3 sentences max)
- Include practical, step-by-step instructions where applicable
- Use headers (##) to break up sections
- Include bullet points and numbered lists
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction
- End with a clear conclusion/summary
- Do NOT include AI disclaimers
- Write as an experienced tech journalist
- Include specific product names, versions, and examples
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly.",
            },
        ],
    )
    return response.choices[0].message.content


def slugify(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    existing = get_existing_titles()
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Easy-to-follow tech guides and tips."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename

if __name__ == '__main__':
    # Every 5th post: generate a Gumroad promo post
    from promo_post import should_write_promo, create_promo_post
    if should_write_promo():
        print("Generating promotional post...")
        filepath, filename = create_promo_post()
    else:
        filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
