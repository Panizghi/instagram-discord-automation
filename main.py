import instaloader
import requests
import pyshorteners
import os
# Instagram account username to monitor
instagram_username = os.environ['INSTAGRAM_USERNAME']

# Discord webhook URL
discord_webhook_url = os.environ['DISCORD_WEBHOOK_URL']

posted_urls = []


# File to store the list of posted URLs
posted_urls_file = "posted_urls.txt"

# Initialize Instaloader
L = instaloader.Instaloader()

# Check for new posts on Instagram
def check_instagram_for_new_post():
    try:
        profile = instaloader.Profile.from_username(L.context, instagram_username)
        post = profile.get_posts()
        latest_post = next(post)
        return latest_post
    except Exception as e:
        print(f"Error checking Instagram: {e}")
        return None

def shorten_url(long_url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(long_url)

# Load the list of posted URLs from the file
def load_posted_urls():
    try:
        with open(posted_urls_file, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Save the list of posted URLs to the file
def save_posted_urls(urls):
    with open(posted_urls_file, "w") as file:
        file.write("\n".join(urls))

# Send the new Instagram post to Discord with a rich embed
def send_instagram_post_to_discord(instagram_post, caption):
    if instagram_post:
        try:
            # Load the list of posted URLs
            posted_urls = load_posted_urls()

            # Check if the post URL has already been posted
            if instagram_post.url not in posted_urls:
                data = {
                    "content": f"Check out the latest post from @{instagram_username} on Instagram!"
                }

                # Create a rich embed with the image
                embed = discord.Embed(
                    title="Instagram Post",
                    description=caption,
                    color=discord.Color.blue()
                )
                # Set the image to the Instagram post image
                embed.set_image(url=instagram_post.url)
                # Set the clickable link to the Instagram profile
                embed.url = "https://instagram.com/uwsmileclub?igshid=MWwxeDdrY2IzZTNmNQ%3D%3D&utm_source=qr"

                data["embeds"] = [embed.to_dict()]

                response = requests.post(discord_webhook_url, json=data)
                if response.status_code == 204:
                    # Add the URL to the list of posted URLs to avoid reposting
                    posted_urls.append(instagram_post.url)
                    # Save the updated list of posted URLs to the file
                    save_posted_urls(posted_urls)
                else:
                    print(f"Error sending to Discord. Status code: {response.status_code}")
            else:
                print("Post already shared on Discord.")
        except Exception as e:
            print(f"Error sending to Discord: {e}")

if __name__ == "__main__":
    latest_post = check_instagram_for_new_post()
    if latest_post:
        send_instagram_post_to_discord(latest_post, latest_post.caption)
    else:
        print("No new Instagram posts found.")
