from clients.forum_client import ForumClient


def main():
    forum_client = ForumClient("jsonplaceholder.typicode.com/")
    print(forum_client.get_posts())


if __name__ == '__main__':
    main()
