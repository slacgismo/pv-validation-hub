import { faker } from '@faker-js/faker';
import LaunchIcon from '@mui/icons-material/Launch';
import ErrorIcon from '@mui/icons-material/Error';
import { Tooltip } from '@mui/material';

export function create_fake_user_data() {
  return {
    _id: faker.datatype.uuid(),
    avatar: faker.image.avatar(),
    email: faker.internet.email(),
    firstName: faker.name.firstName(),
    lastName: faker.name.lastName(),
    location: `${faker.address.city()}, ${faker.address.stateAbbr()}`,
    subscriptionTier: faker.helpers.arrayElement(['admin', 'developer', 'viewer']),
    github: 'https://github.com/aks2297',
  };
}

export function create_fake_submission_row(ranking_number) {
  const analysis_id = faker.datatype.number();
  const ranking_id = faker.datatype.number();
  const developer_name = faker.name.firstName();
  const score = faker.datatype.number();
  const submit_time = faker.helpers.arrayElement([
    `${faker.datatype.number({ min: 1, max: 23 })}h`,
    `${faker.datatype.number({ min: 1, max: 30 })}d`,
  ]);
  const execution_time = faker.helpers.arrayElement([
    `${faker.datatype.number({ min: 1, max: 23 })}h`,
    `${faker.datatype.number({ min: 1, max: 30 })}d`,
  ]);
  const error = <Tooltip title="Error-Failed"><ErrorIcon /></Tooltip>;
  const algorithm_url = <a href={faker.internet.url()}><LaunchIcon /></a>;
  return {
    analysis_id,
    ranking_id,
    developer_name,
    score,
    submit_time,
    execution_time,
    error,
    algorithm_url,
  };
}

export function create_fake_submission_array(number) {
  const fake_array = [];
  for (let val = 0; val < number; val++) {
    fake_array[val] = create_fake_submission_row(val + 1);
  }
  return fake_array;
}

export function create_fake_leaderboard_row(ranking_number) {
  const developer_group = faker.name.fullName();
  const created_by = developer_group;
  const algorithm = 'time shift algorithm';
  const score = faker.datatype.number();
  const submission = <a href={faker.internet.url()}><LaunchIcon /></a>;
  const last_updated = faker.helpers.arrayElement([
    `${faker.datatype.number({ min: 1, max: 23 })}h`,
    `${faker.datatype.number({ min: 1, max: 30 })}d`,
  ]);
  return {
    ranking_number,
    developer_group,
    score,
    submission,
    last_updated,
    created_by,
    algorithm,
  };
}

export function create_fake_leaderboard_array(number) {
  const fake_array = [];
  for (let val = 0; val < number; val++) {
    fake_array[val] = create_fake_leaderboard_row(val + 1);
  }
  return fake_array;
}

export function create_fake_analysis_data() {
  return {
    id: faker.datatype.uuid(),
    title: `Ananlysis_${faker.random.word()}`,
    sub_title: `Sub Analysis ${faker.random.word()}`,
    image: faker.image.image(),
    description: faker.lorem.sentence(8),
    user_id: faker.datatype.uuid(),
    user_avatar: faker.image.avatar(),
    user_initial: faker.random.alpha(1).toUpperCase(),
  };
}

export function create_fake_analysis_big_image_data() {
  return {
    id: faker.datatype.uuid(),
    title: `Ananlysis_${faker.random.word()}`,
    sub_title: `Sub Analysis ${faker.random.word()}`,
    image: faker.image.animals(1200, 200),
    description: faker.lorem.sentence(8),
    user_id: faker.datatype.uuid(),
    user_avatar: faker.image.avatar(),
    user_initial: faker.random.alpha(1).toUpperCase(),
  };
}

export function create_fake_analysis_data_array(number) {
  const fake_array = [];
  for (let val = 0; val < number; val++) {
    fake_array[val] = create_fake_analysis_data();
  }
  return fake_array;
}

export function create_fake_dataset_descrption() {
  return {
    description: faker.lorem.lines(20),
    train_data: faker.lorem.sentences(5),
    test_data: faker.lorem.sentences(5),
    final_note: faker.lorem.sentences(4),
    file: `${faker.internet.url()}/test_pv.zip`,
    number_of_files: 3,
    type_of_files: 'csv',
  };
}

export function create_fake_overview() {
  return {
    description: faker.lorem.lines(200),
    title: faker.lorem.sentence(),
    media: faker.image.business(),
    number_of_submission: faker.datatype.number({ min: 4560, max: 80000 }),
    number_of_developers: faker.datatype.number({ min: 160, max: 50000 }),
    users_points: 0,
    users_ranking: 0,
  };
}

export function create_fake_ruleset() {
  return {
    description: faker.lorem.lines(30),
    title: faker.lorem.sentence(),
    media: faker.image.business(),
  };
}

export function create_fake_image_array_list(number) {
  const fake_array = {};
  fake_array.juliusomo = faker.image.avatar();
  for (let val = 0; val < number; val++) {
    fake_array[faker.name.firstName] = faker.image.avatar();
  }
  return fake_array;
}

export function create_fake_comment(number) {
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
export function create_fake_reply_comment(number) {
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

export function fake_reply_array(number, count, replyingTo) {
  const fake_array = [];
  let temp_count = count;
  for (let i = 0; i < number; i++) {
    const temp = create_fake_reply_comment(temp_count);
    temp.replyingTo = replyingTo;
    fake_array[i] = temp;
    temp_count += 1;
  }
  return [fake_array, temp_count - 1];
}

export function fake_comments_array(number) {
  const fake_array = [];
  let count = 1;
  for (let val = 0; val < number; val++) {
    const temp = create_fake_comment(count);
    if (val % 4 === 0) {
      [temp.replies, count] = fake_reply_array(faker.helpers.arrayElement([3, 5, 4]), count, temp.user.username);
    }
    fake_array[val] = temp;
    count += 1;
  }
  return fake_array;
}

export function fake_discussion_output(analysis_id, user_id, number) {
  return {
    currentUser: {
      image: faker.image.avatar(),
      username: user_id,
    },
    comments: fake_comments_array(number),
  };
}
export function fake_date_between_output(number) {
  let date_array = [];
  for (let i = 0; i < number; i++) {
    date_array[i] = new Date(faker.date.between('2020-01-01T00:00:00.000Z', '2023-01-01T00:00:00.000Z')).toDateString();
  }
  date_array = date_array.sort((a, b) => new Date(a) - new Date(b));
  return date_array;
}

export function fake_number_of_submission(number) {
  const submission_array = [];
  for (let i = 0; i < number; i++) {
    submission_array[i] = faker.datatype.number({ min: 2, max: 25 });
  }
  return submission_array;
}

export function fake_submission_details() {
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

export function fake_highlight() {
  return {
    heading: faker.lorem.words(2),
    description: faker.lorem.words(20),
  };
}

export function fake_homepage_note() {
  const homepage_highlights = [];
  for (let i = 0; i < 4; i++) {
    homepage_highlights[i] = fake_highlight();
  }
  return homepage_highlights;
}
export function fake_homepage_validation_gist() {
  return faker.lorem.lines(4);
}
