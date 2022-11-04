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
        _id: faker.datatype.uuid(),
        avatar: faker.image.avatar(),
        description: faker.lorem.sentence(8)
    };
}

export function create_fake_analysis_data_array(number){
    var fake_array = [];
    for(let val = 0; val < number; val++){
        fake_array[val] = create_fake_analysis_data();
    }
    return fake_array;
}