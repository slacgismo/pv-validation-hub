const generatePersonsData = (number) => {
    const persons = [];
    while (number >= 0) {
        persons.push({
            id: number,
            name: faker.name.firstName(),
            description: faker.lorem.paragraphs(2),
            picture: faker.image.avatar()
        });
        number--;
    }
    return persons;
};

const creatrFakeUsers = () => {
    return generatePersonsData(20);
}

export const getUserData = (number) => {
    return creatrFakeUsers();
}

