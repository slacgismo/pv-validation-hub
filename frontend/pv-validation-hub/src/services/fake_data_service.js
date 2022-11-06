import { faker } from "@faker-js/faker"

export function create_fake_user_data(){
    return {
        _id: faker.datatype.uuid(),
        avatar: faker.image.avatar(),
        email: faker.internet.email(),
        firstName: faker.name.firstName(),
        lastName: faker.name.lastName(),
        subscriptionTier: faker.helpers.arrayElement(['admin', 'developer', 'viewer']),
      };
}

export function create_fake_analysis_data(){
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

export function create_fake_analysis_data_array(number){
    var fake_array = [];
    for(let val = 0; val < number; val++){
        let fake_data = create_fake_analysis_data();
        console.log(fake_data);
        fake_array[val] = fake_data;
    }
    return fake_array;
}