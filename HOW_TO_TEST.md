# Quiz API Testing Guide

This document provides a comprehensive guide on how to test the Quiz API application using curl commands. The application allows users to create quizzes, send invitations, and participate in quizzes.

## Prerequisites

- The application should be running on `http://localhost:8000`
- You need at least 2 user accounts for testing the invitation workflow
- All requests (except registration and login) require JWT authentication

## Base URL

```
http://localhost:8000/api/v1/
```

## Testing Workflow

### 1. User Registration and Authentication

#### 1.1 Register First User (Quiz Creator)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "creator_user",
    "email": "creator@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Creator"
  }'
```

#### 1.2 Register Second User (Quiz Participant)
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "participant_user",
    "email": "participant@example.com",
    "password": "securepassword123",
    "first_name": "Jane",
    "last_name": "Participant"
  }'
```

#### 1.3 Login (Alternative to Registration)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "creator_user",
    "password": "securepassword123"
  }'
```

#### 1.4 Get User Profile
```bash
curl -X GET http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Quiz Management

#### 2.1 Create a Quiz (as Creator)
```bash
curl -X POST http://localhost:8000/api/v1/quizzes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CREATOR_ACCESS_TOKEN" \
  -d '{
    "title": "JavaScript Basics Quiz",
    "description": "Test your knowledge of JavaScript fundamentals",
    "questions": [
      {
        "text": "What is the correct syntax for creating a function in JavaScript?",
        "order": 1,
        "points": 10,
        "answers": [
          {
            "text": "function myFunction() {}",
            "is_correct": true,
            "order": 1
          },
          {
            "text": "def myFunction() {}",
            "is_correct": false,
            "order": 2
          },
          {
            "text": "func myFunction() {}",
            "is_correct": false,
            "order": 3
          }
        ]
      },
      {
        "text": "Which of the following is a JavaScript data type?",
        "order": 2,
        "points": 5,
        "answers": [
          {
            "text": "String",
            "is_correct": true,
            "order": 1
          },
          {
            "text": "Integer",
            "is_correct": false,
            "order": 2
          },
          {
            "text": "Character",
            "is_correct": false,
            "order": 3
          }
        ]
      }
    ]
  }'
```

#### 2.2 Get Quiz Details (As a creator, invited or participant)
```bash
curl -X GET http://localhost:8000/api/v1/quizzes/QUIZ_UUID/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 2.3 Get User's Quizzes (Quizzes the user can participate in or has already participated in)
```bash
curl -X GET http://localhost:8000/api/v1/quizzes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 2.4 Get Creator's Quizzes (Quizzes created by the user)
```bash
curl -X GET http://localhost:8000/api/v1/creators/CREATOR_UUID/quizzes/ \
  -H "Authorization: Bearer YOUR_CREATOR_ACCESS_TOKEN"
```

### 3. Invitation Management

#### 3.1 Send Quiz Invitation (as Creator)
```bash
curl -X POST http://localhost:8000/api/v1/quizzes/QUIZ_UUID/invitations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CREATOR_ACCESS_TOKEN" \
  -d '{
    "participant_email": "participant@example.com"
  }'
```


#### 3.2 Accept Quiz Invitation (as Participant)
```bash
curl -X POST http://localhost:8000/api/v1/invitations/INVITATION_UUID/accept/ \
  -H "Authorization: Bearer YOUR_PARTICIPANT_ACCESS_TOKEN"
```

### 4. Quiz ParticipationData

#### 4.1 Submit Quiz Answers (as Participant)
```bash
curl -X POST http://localhost:8000/api/v1/quizzes/QUIZ_UUID/submit/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_PARTICIPANT_ACCESS_TOKEN" \
  -d '{
    "answers": [
      {
        "question_id": 1,
        "answer_id": 1
      },
      {
        "question_id": 2,
        "answer_id": 5
      }
    ]
  }'
```

#### 4.2 Get My Quiz Progress (as Participant)
This endpoint allows participants to check their own progress and results for a specific quiz.

```bash
curl -X GET http://localhost:8000/api/v1/quizzes/QUIZ_UUID/progress/ \
  -H "Authorization: Bearer YOUR_PARTICIPANT_ACCESS_TOKEN"
```


### 5. Quiz Results

#### 5.1 Get Quiz Scores (as Creator)
```bash
curl -X GET http://localhost:8000/api/v1/quizzes/QUIZ_UUID/scores/ \
  -H "Authorization: Bearer YOUR_CREATOR_ACCESS_TOKEN"
```

#### 5.2 Get Creator Quiz Progress (as Creator)
This endpoint provides comprehensive progress metrics for quiz creators to monitor their quiz performance.

```bash
curl -X GET http://localhost:8000/api/v1/quizzes/QUIZ_UUID/creator-progress/ \
  -H "Authorization: Bearer YOUR_CREATOR_ACCESS_TOKEN"
```



### 6. Authentication Management

#### 6.1 Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

#### 6.2 Verify Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_ACCESS_TOKEN"
  }'
```

#### 6.3 Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

## Managing Test Variables

For easier testing, set these variables in your shell to avoid copying/pasting tokens and IDs:

```bash
# Set after user registration
export CREATOR_TOKEN="your_creator_access_token_here"
export PARTICIPANT_TOKEN="your_participant_access_token_here"

# Set after quiz creation
export QUIZ_ID="your_quiz_uuid_here"

# Set after sending invitation
export INVITATION_ID="your_invitation_uuid_here"

# Set creator and participant UUIDs (from registration/profile responses)
export CREATOR_UUID="your_creator_uuid_here"
export PARTICIPANT_UUID="your_participant_uuid_here"
```

Then you can use these variables in your curl commands:
```bash
# Example: Get quiz details
curl -X GET http://localhost:8000/api/v1/quizzes/$QUIZ_ID/ \
  -H "Authorization: Bearer $CREATOR_TOKEN"

# Example: Send invitation
curl -X POST http://localhost:8000/api/v1/quizzes/$QUIZ_ID/invitations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CREATOR_TOKEN" \
  -d '{"participant_email": "participant@example.com"}'

# Example: Get creator quiz progress
curl -X GET http://localhost:8000/api/v1/quizzes/$QUIZ_ID/creator-progress/ \
  -H "Authorization: Bearer $CREATOR_TOKEN"

# Example: Get my quiz progress as participant
curl -X GET http://localhost:8000/api/v1/quizzes/$QUIZ_ID/progress/ \
  -H "Authorization: Bearer $PARTICIPANT_TOKEN"
```

## Complete Testing Scenario

Here's a complete end-to-end testing scenario:

### Step 1: Setup Users
1. Register creator user
2. Register participant user
3. Save both access tokens

### Step 2: Create and Manage Quiz
1. Create a quiz using creator's token
2. Save the quiz UUID from response
3. Get quiz details to verify creation

### Step 3: Invitation Process
1. Send invitation to participant using creator's token
2. Save invitation UUID from response
3. Accept invitation using participant's token

### Step 4: Quiz ParticipationData
1. Get quiz details using participant's token (should now have access)
2. Submit answers using participant's token
3. Verify submission response
4. Check participant's own progress and score

### Step 5: Results and Progress Monitoring
1. Get quiz scores using creator's token
2. Verify participant's score is listed
3. Get creator quiz progress to monitor invitation and participation metrics
4. Verify invitation acceptance rate and completion statistics

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful GET/POST operations
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Server error

## Notes

1. **Authentication**: All endpoints except registration and login require JWT authentication
2. **UUIDs**: Replace `QUIZ_UUID`, `INVITATION_UUID`, etc. with actual UUIDs from responses
3. **Tokens**: Replace `YOUR_ACCESS_TOKEN` with actual tokens from login/registration responses
4. **Permissions**: Only quiz creators can send invitations and view scores
5. **Question/Answer IDs**: These are auto-generated integers, use the actual IDs from quiz creation response

## Environment Setup

Make sure your application is running with:
```bash
docker-compose up
```
