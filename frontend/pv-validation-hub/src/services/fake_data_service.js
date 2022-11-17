import { faker } from "@faker-js/faker"
import LaunchIcon from '@mui/icons-material/Launch';

export function create_fake_user_data() {
    return {
        _id: faker.datatype.uuid(),
        avatar: faker.image.avatar(),
        email: faker.internet.email(),
        firstName: faker.name.firstName(),
        lastName: faker.name.lastName(),
        subscriptionTier: faker.helpers.arrayElement(['admin', 'developer', 'viewer']),
    };
}

export function create_fake_leaderboard_row(ranking_number) {
    let developer_name = faker.name.firstName();
    let score = faker.datatype.number();
    let entries = faker.datatype.number();
    let last_updated = faker.helpers.arrayElement([
        faker.datatype.number({ 'min': 1, 'max': 23 }) + 'h',
        faker.datatype.number({ 'min': 1, 'max': 30 }) + 'd'
    ]);
    let code_url = <a href={faker.internet.url()}><LaunchIcon/></a>;
    return {
        ranking_number,
        developer_name,
        score,
        entries,
        last_updated,
        code_url
    }
}

export function create_fake_leaderboard_array(number) {
    var fake_array = [];
    for (let val = 0; val < number; val++) {
        fake_array[val] = create_fake_leaderboard_row(val + 1);
    }
    return fake_array;
}

export function create_fake_analysis_data() {
    return {
        id: faker.datatype.uuid(),
        title: "Ananlysis_" + faker.random.word(),
        sub_title: "Sub Analysis " + faker.random.word(),
        image: faker.image.image(),
        description: faker.lorem.sentence(8),
        user_id: faker.datatype.uuid(),
        user_avatar: faker.image.avatar(),
        user_initial: faker.random.alpha(1).toUpperCase()
    };
}

export function create_fake_analysis_big_image_data() {
    return {
        id: faker.datatype.uuid(),
        title: "Ananlysis_" + faker.random.word(),
        sub_title: "Sub Analysis " + faker.random.word(),
        image: faker.image.animals(1200,120),
        description: faker.lorem.sentence(8),
        user_id: faker.datatype.uuid(),
        user_avatar: faker.image.avatar(),
        user_initial: faker.random.alpha(1).toUpperCase()
    };
}

export function create_fake_analysis_data_array(number) {
    var fake_array = [];
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
        file: faker.internet.url() + "/test_pv.zip",
        number_of_files: 3,
        type_of_files: "csv"
    }
}

export function create_fake_overview() {
    return {
        description: faker.lorem.lines(200),
        title: faker.lorem.sentence(),
        media: faker.image.business(),
        number_of_submission: faker.datatype.number({'min':4560,'max':80000}),
        number_of_developers: faker.datatype.number({'min':160,'max':50000}),
        users_points: 0,
        users_ranking: 0
    }
}