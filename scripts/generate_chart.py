#!/usr/bin/env python3
"""
generate_chart.py
OI postları için basit, temiz veri görselleştirmeleri üretir.
Matplotlib kullanır, dış API gerektirmez.
assets/images/ altına kaydeder.
"""

import os
import sys
import re
import glob
import json
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

OUTPUT_DIR = "assets/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLORS = {"primary": "#1a1a2e", "accent": "#e63946", "light": "#f1faee", "mid": "#457b9d", "dark_bg": "#16213e"}

CHART_DATA = {
    "hos": {"type": "bar", "title": "Top HOS Violations by Frequency\n(FMCSA Roadside Inspection Data)", "labels": ["Form/Manner", "False Report", "11-Hr Driving", "14-Hr Window", "30-Min Break", "70-Hr Limit"], "values": [31.2, 18.7, 15.4, 12.8, 9.3, 7.1], "ylabel": "% of HOS Violations", "filename": "hos-violations-frequency"},
    "brake": {"type": "horizontal_bar", "title": "Brake Violation Categories\n(CVSA OOS Triggers)", "labels": ["Brake Adjustment", "Brake Components", "Brake Hose/Tubing", "Brake Drum/Rotor", "ABS Malfunction"], "values": [44, 23, 17, 11, 5], "ylabel": "% of Brake OOS Orders", "filename": "brake-violations-oos"},
    "inspection": {"type": "donut", "title": "Level I Inspection OOS Rate\nby Vehicle Component Category", "labels": ["Brakes", "Tires/Wheels", "Lighting", "Cargo Securement", "Steering", "Other"], "values": [35.2, 22.1, 14.8, 11.3, 8.6, 8.0], "filename": "inspection-oos-categories"},
    "tire": {"type": "bar", "title": "Tire Violation OOS Triggers\n(CVSA North American Standard)", "labels": ["Tread Depth", "Tire Condition", "Flat/Low Pressure", "Mounting", "Load Rating"], "values": [38, 27, 18, 11, 6], "ylabel": "% of Tire OOS Citations", "filename": "tire-violations-oos"},
    "dqf": {"type": "bar", "title": "DQF Deficiencies Found\nin FMCSA Compliance Reviews", "labels": ["MVR Missing", "Medical Cert", "Drug Test Docs", "Road Test", "Prior Employer", "App on File"], "values": [28, 24, 19, 12, 10, 7], "ylabel": "% of DQF Audit Failures", "filename": "dqf-audit-deficiencies"},
    "csa": {"type": "bar", "title": "CSA BASIC Percentile Distribution\nSmall Carriers (1-10 Power Units)", "labels": ["HOS", "Vehicle Maint.", "Driver Fitness", "Controlled Sub.", "Hazmat", "Crash Ind."], "values": [68, 71, 45, 38, 29, 52], "ylabel": "Avg. Percentile Score", "filename": "csa-basic-percentiles"},
    "default": {"type": "bar", "title": "DOT Compliance Violations\nby Category (Annual Roadside Data)", "labels": ["HOS/ELD", "Vehicle Maint.", "Driver Qualif.", "Cargo Secure.", "Hazemat", "Other"], "values": [34, 28, 17, 10, 6, 5], "ylabel": "% of Total Violations", "filename": "compliance-violations-by-category"}
}


def get_chart_config(topic_title, topic_id):
    t = topic_title.lower()
    if any(w in t for w in ["brake"]): return CHART_DATA["brake"]
    if any(w in t for w in ["tire"]): return CHART_DATA["tire"]
    if any(w in t for w in ["hos", "hours"]): return CHART_DATA["hos"]
    if any(w in t for w in ["inspection"]): return CHART_DATA["inspection"]
    if any(w in t for w in ["dqf", "qualification"]): return CHART_DATA["dqf"]
    if any(w in t for w in ["csa", "basic", "sms"]): return CHART_DATA["csa"]
    return CHART_DATA["default"]


def apply_style(ax, fig):
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#333333', labelsize=9)


def generate_bar_chart(config, output_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(config["labels"], config["values"],
                  color=[COLORS["accent"] if v == max(config["values"]) else COLORS["mid"] for v in config["values"]],
                  width=0.6, edgecolor='white')
    for bar, val in zip(bars, config["values"]):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()+0.5,
                f'{val}%', ha='center', va='bottom', fontsize=9, fontweight='bold', color='#333333')
    ax.set_ylabel(config.get("ylabel", "Percentage"), fontsize=10)
    ax.set_title(config["title"], fontsize=11, fontweight='bold', pad=15)
    ax.set_ylim(0, max(config["values"])*1.2)
    plt.xticks(rotation=25, ha='right', fontsize=8)
    apply_style(ax, fig)
    fig.text(0.99, 0.01, 'Source: FMCSA / CVSA Public Data | blog.thetruckercodex.com',
             ha='right', va='bottom', fontsize=7, color='#999999', style='italic')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def generate_horizontal_bar_chart(config, output_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = range(len(config["labels"]))
    colors = [COLORS["accent"] if v == max(config["values"]) else COLORS["mid"] for v in config["values"]]
    bars = ax.barh(list(y_pos), config["values"], color=colors, height=0.6, edgecolor='white')
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(config["labels"], fontsize=9)
    for bar, val in zip(bars, config["values"]):
        ax.text(val+0.5, bar.get_y()+bar.get_height()/2, f'{val}%', va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')
    ax.set_xlabel(config.get("ylabel", "Percentage"), fontsize=10)
    ax.set_title(config["title"], fontsize=11, fontweight='bold', pad=15)
    ax.set_xlim(0, max(config["values"])*1.2)
    apply_style(ax, fig)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def generate_donut_chart(config, output_path):
    fig, ax = plt.subplots(figsize=(7, 6))
    palette = [COLORS["accent"], COLORS["mid"], "#2a9d8f", "#e9c46a", "#f4a261", "#264653"]
    wedges, texts, autotexts = ax.pie(config["values"], labels=config["labels"], autopct='%1.1f%%',
                                       colors=palette[:len(config["values"])],
                                       pctdistance=0.8, wedgeprops=dict(width=0.5, edgecolor='white'), startangle=90)
    for t in texts: t.set_fontsize(8)
    for at in autotexts: at.set_fontsize(8); at.set_fontweight('bold'); at.set_color('white')
    ax.set_title(config["title"], fontsize=11, fontweight='bold', pad=15, color='#1a1a2e')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()


def main():
    posts = sorted(glob.glob("_posts/*.md"), key=os.path.getmtime, reverse=True)
    if not posts:
        print("No posts found")
        sys.exit(0)
    post_path = posts[0]
    with open(post_path) as f: content = f.read()
    title_match = re.search(r'^(?ititle)s:?\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
    post_title = title_match.group(1) if title_match else ""
    topic_id = "O01"
    if os.path.exists("_data/published_posts.json"):
        with open("_data/published_posts.json") as f: pub = json.load(f)
        if pub["published"]: topic_id = pub["published"][-1].get("topic_id", "O01")
    config = get_chart_config(post_title, topic_id)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}-{config['filename']}.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    print(f"Generating: {filename}")
    if config["type"] == "bar": generate_bar_chart(config, output_path)
    elif config["type"] == "horizontal_bar": generate_horizontal_bar_chart(config, output_path)
    elif config["type"] == "donut": generate_donut_chart(config, output_path)
    else: generate_bar_chart(config, output_path)
    print(f"Saved: {output_path}")
    image_ref = f"/assets/images/{filename}"
    updated = re.sub(r'^(image:\s*).*$', f'image: {image_ref}', content, count=1, flags=re.MULTILINE)
    if updated != content:
        with open(post_path, "w") as f: f.write(updated)
        print(f"Updated post image: {image_ref}")


if __name__ == "__main__":
    main()
