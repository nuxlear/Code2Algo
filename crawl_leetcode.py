import scrapy
import requests
from selenium import webdriver

import json
import os
from pathlib import Path


official_solution_query = """
query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) {
  questionSolutions(
    filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags}
  ) {
    hasDirectResults
    totalNum
    solutions {
      id
      title
      commentCount
      topLevelCommentCount
      viewCount
      pinned
      isFavorite
      solutionTags {
        name
        slug
      }
      post {
        id
        status
        voteCount
        creationDate
        isHidden
        author {
          username
          isActive
          nameColor
          activeBadge {
            displayName
            icon
          }
          profile {
            userAvatar
            reputation
          }
        }
      }
      searchMeta {
        content
        contentType
        commentAuthor {
          username
        }
        replyAuthor {
          username
        }
        highlights
      }
    }
  }
}
    """

community_solution_query = """
query communitySolutions($questionSlug: String!, $skip: Int!, $first: Int!, $query: String, $orderBy: TopicSortingOption, $languageTags: [String!], $topicTags: [String!]) {
  questionSolutions(
    filters: {questionSlug: $questionSlug, skip: $skip, first: $first, query: $query, orderBy: $orderBy, languageTags: $languageTags, topicTags: $topicTags}
  ) {
    hasDirectResults
    totalNum
    solutions {
      id
      title
      commentCount
      topLevelCommentCount
      viewCount
      pinned
      isFavorite
      solutionTags {
        name
        slug
      }
      post {
        id
        status
        voteCount
        content
        creationDate
        isHidden
        author {
          username
          isActive
          nameColor
          activeBadge {
            displayName
            icon
          }
          profile {
            userAvatar
            reputation
          }
        }
      }
      searchMeta {
        content
        contentType
        commentAuthor {
          username
        }
        replyAuthor {
          username
        }
        highlights
      }
    }
  }
}
    """

question_content_query = """
query questionContent($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    content
    mysqlSchemas
  }
}
    """

"""
    query communitySolution($topicId: Int!) {
  isSolutionTopic(id: $topicId)
  topic(id: $topicId) {
    id
    viewCount
    topLevelCommentCount
    favoriteCount
    subscribed
    title
    pinned
    solutionTags {
      name
      slug
    }
    hideFromTrending
    commentCount
    isFavorite
    post {
      id
      voteCount
      voteStatus
      content
      updationDate
      creationDate
      status
      isHidden
      author {
        isDiscussAdmin
        isDiscussStaff
        username
        nameColor
        activeBadge {
          displayName
          icon
        }
        profile {
          userAvatar
          reputation
        }
        isActive
      }
      authorIsModerator
      isOwnPost
    }
  }
  relatedSolutions(topicId: $topicId) {
    id
    post {
      author {
        username
        profile {
          userAvatar
        }
      }
    }
    title
    solutionTags {
      name
      slug
    }
  }
}
    """


if __name__ == '__main__':
    # response = requests.post('https://www.leetcode.com/graphql/',
    #                          headers={'Content-Type': 'application/json'},
    #                          data=tmp)

    output_dir = Path('leetcode_solutions')
    os.makedirs(output_dir, exist_ok=True)

    response = requests.get('https://leetcode.com/api/problems/all/')
    problems = json.loads(response.text)['stat_status_pairs']

    for s, stat in enumerate(problems):
        question_id = stat['stat']['question_id']
        question_slug = stat['stat']['question__title_slug']

        response = requests.get('https://www.leetcode.com/graphql/',
                                params={
                                    'query': question_content_query,
                                    'variables': json.dumps({
                                        'titleSlug': question_slug,
                                    }, indent=2)
                                })
        if response.status_code != 200:
            print(f'Error! on `{question_slug}` [{question_id}] - {response.status_code}')
            continue
        d = json.loads(response.text)
        question_content = d['data']['question']['content']

        print(f'({s}/{len(problems)}) Getting solutions from `{question_slug}` [{question_id}]... ', end='')
        response = requests.get('https://www.leetcode.com/graphql/',
                                params={
                                    'query': community_solution_query,
                                    'variables': json.dumps({
                                        'orderBy': 'hot',
                                        'languageTags': ['python3'],
                                        'questionSlug': question_slug,
                                        'skip': 0,
                                        'first': 100,
                                    }, indent=2)
                                })
        d = json.loads(response.text)
        solutions = d['data']['questionSolutions']['solutions']
        if len(solutions) == 0:
            print('Skipped with no solutions. ')
            continue

        qinfo = {
            'question_id': question_id,
            'question_slug': question_slug,
            'question_content': question_content,
            'solutions': []
        }
        for solution in solutions:
            solution_id = solution['id']
            solution_content = solution['post']['content'].replace('\\n', '\n')
            qinfo['solutions'].append({
                'solution_id': solution_id,
                'solution_content': solution_content,
            })

        print(f' -> Found {len(qinfo["solutions"])} solutions. ')
        with open(output_dir / f'{question_id}_{question_slug}.json', 'w', encoding='utf-8') as f:
            json.dump(qinfo, f, indent=4, ensure_ascii=False)
