import { fake_homepage_note, fake_homepage_validation_gist } from "./fake_data_service"

export const HomepageService = {
    getHighlights() {
        return fake_homepage_note();
    },

    getValidationHubGist() {
        return fake_homepage_validation_gist();
    }
}