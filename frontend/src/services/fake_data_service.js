// eslint-disable-next-line import/no-extraneous-dependencies
import { faker } from '@faker-js/faker';

export function createFakeImageArrayList(number) {
  const fakeArray = {};
  fakeArray.juliusomo = faker.image.avatar();
  for (let val = 0; val < number; val += 1) {
    fakeArray[faker.name.firstName] = faker.image.avatar();
  }
  return fakeArray;
}

export function createFakeComment(number) {
  return {
    id: number,
    content: faker.lorem.sentences(2),
    createdAt: faker.helpers.arrayElement([
      `${faker.datatype.number({ min: 1, max: 23 })}hours ago`,
      `${faker.datatype.number({ min: 1, max: 30 })}days ago`,
    ]),
    user: {
      image: faker.image.avatar(),
      username: faker.name.fullName(),
    },
    replies: [],
  };
}
export function createFakeReplyComment(number) {
  return {
    id: number,
    content: faker.lorem.sentences(2),
    createdAt: faker.helpers.arrayElement([
      `${faker.datatype.number({ min: 1, max: 23 })}hours ago`,
      `${faker.datatype.number({ min: 1, max: 30 })}days ago`,
    ]),
    user: {
      image: faker.image.avatar(),
      username: faker.name.fullName(),
    },
    replyingTo: '',
  };
}

export function fakeReplyArray(number, count, replyingTo) {
  const fakeArray = [];
  let tempCount = count;
  for (let i = 0; i < number; i += 1) {
    const temp = createFakeReplyComment(tempCount);
    temp.replyingTo = replyingTo;
    fakeArray[i] = temp;
    tempCount += 1;
  }
  return [fakeArray, tempCount - 1];
}

export function fakeCommentsArray(number) {
  const fakeArray = [];
  let count = 1;
  for (let val = 0; val < number; val += 1) {
    const temp = createFakeComment(count);
    if (val % 4 === 0) {
      [temp.replies, count] = fakeReplyArray(
        faker.helpers.arrayElement([3, 5, 4]),
        count,
        temp.user.username,
      );
    }
    fakeArray[val] = temp;
    count += 1;
  }
  return fakeArray;
}

export function fakeDiscussionOutput(analysisId, userId, number) {
  return {
    currentUser: {
      image: faker.image.avatar(),
      username: userId,
    },
    comments: fakeCommentsArray(number),
  };
}
export function fakeDateBetweenOutput(number) {
  let dateArray = [];
  for (let i = 0; i < number; i += 1) {
    dateArray[i] = new Date(faker.date.between('2020-01-01T00:00:00.000Z', '2023-01-01T00:00:00.000Z')).toDateString();
  }
  dateArray = dateArray.sort((a, b) => new Date(a) - new Date(b));
  return dateArray;
}

export function fakeNumberOfSubmission(number) {
  const submissionArray = [];
  for (let i = 0; i < number; i += 1) {
    submissionArray[i] = faker.datatype.number({ min: 2, max: 25 });
  }
  return submissionArray;
}

export function fakeSubmissionDetails() {
  return {
    user_id: faker.datatype.uuid,
    user_name: faker.datatype.username,
    successful_submissions: faker.datatype.number({ min: 10, max: 70 }),
    successful_submissions_change: faker.datatype.number({ min: -50, max: 70 }),
    errored_submissions: faker.datatype.number({ min: 10, max: 70 }),
    errored_submissions_change: faker.datatype.number({ min: -50, max: 70 }),
    total_submissions: faker.datatype.number({ min: 100, max: 150 }),
    total_submissions_change: faker.datatype.number({ min: -50, max: 70 }),
    score: faker.datatype.number(),
    score_change: faker.datatype.number({ min: 0, max: 70 }),

  };
}

export function fakeHighlight() {
  return {
    heading: faker.lorem.words(2),
    description: faker.lorem.words(20),
  };
}

export function fakeHomepageNote() {
  const homepageHighlights = [];
  for (let i = 0; i < 4; i += 1) {
    homepageHighlights[i] = fakeHighlight();
  }
  return homepageHighlights;
}
export function fakeHomepageValidationGist() {
  return faker.lorem.lines(4);
}
