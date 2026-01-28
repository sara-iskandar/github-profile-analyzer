from flask import Flask, request, render_template
import requests


app = Flask(__name__)

def get_github_user(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_user_repos(username):
    repos = f"https://api.github.com/users/{username}/repos?per_page=100"
    response = requests.get(repos)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def analyze_profile(user_data, repos):
    total_stars = 0
    total_forks = 0
    languages = set()
    most_popular = None
    max_stars = 0

    for repo in repos:
        total_stars += repo['stargazers_count']
        total_forks += repo['forks_count']

        if repo['language']:
            languages.add(repo['language'])

        if repo['stargazers_count'] > max_stars:
            max_stars = repo['stargazers_count']
            most_popular = repo['name']

    return {
        'username': user_data['login'],
        'avatar': user_data['avatar_url'],
        'name': user_data['name'],
        'bio': user_data['bio'],
        'followers': user_data['followers'],
        'following': user_data['following'],
        'public_repos': user_data['public_repos'],
        'total_stars': total_stars,
        'total_forks': total_forks,
        'languages': list(languages),
        'most_popular_repo': most_popular
    }


def calculate_score(analysis):
    score = 0

    if analysis['bio']:
        score += 20

    if analysis['public_repos'] >= 5:
        score += 10

    if analysis['followers'] >= 10:
        score += 10

    if len(analysis['languages']) >= 3:
        score += 20

    if analysis['following'] >= 10:
        score += 20

    if analysis['total_stars'] >= 10:
        score += 20

    return min(score, 100)


def generate_roast(analysis):
    roasts = []

    if not analysis['bio']:
        roasts.append("No bio? Too mysterious or just nothing interesting to say?")

    if analysis['followers'] == 0:
        roasts.append("Zero followers. Even your mom didn't hit that follow button.")

    if analysis['total_stars'] == 0:
        roasts.append("Not a single star. Your repos are lonelier than a mass farmer's social life.")

    if analysis['public_repos'] > 20 and analysis['total_stars'] < 10:
        roasts.append(f"{analysis['public_repos']} repos and barely any stars? Quantity over quality isn't working.")

    if analysis['following'] > analysis['followers'] * 2 and analysis['following'] > 50:
        roasts.append("Following way more people than follow you back. Desperate much?")

    if len(analysis['languages']) == 1:
        roasts.append(f"Only {analysis['languages'][0]}? One-trick pony alert.")

    if len(analysis['languages']) == 0:
        roasts.append("No languages detected. Are you even coding or just collecting empty repos?")

    if not analysis['most_popular_repo']:
        roasts.append("No standout project. Everything you built is equally... forgettable.")

    if analysis['public_repos'] < 3:
        roasts.append("Less than 3 public repos? GitHub isn't just for storing dotfiles.")

    if analysis['followers'] > 100 and analysis['total_stars'] < 20:
        roasts.append("Big follower count, tiny star count. Are you an influencer or a developer?")

    if analysis['total_forks'] > analysis['total_stars']:
        roasts.append("More forks than stars. People take your code and run — but never say thanks.")

    if not roasts:
        return "Damn, your profile is actually solid. I tried to roast you but you're doing great. Keep it up. 👏"

    return " ".join(roasts)


@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    error = None

    if request.method == 'POST':
        username = request.form.get('username').strip()

        user = get_github_user(username)

        if user:
            repos = get_user_repos(username)
            analysis = analyze_profile(user, repos)
            score = calculate_score(analysis)
            analysis['score'] = score
            analysis['roast'] = generate_roast(analysis)
            result = analysis
        else:
            error = f"User '{username}' not found"

    return render_template('index.html', result=result, error=error)


if __name__ == '__main__':
    app.run(debug=True)
