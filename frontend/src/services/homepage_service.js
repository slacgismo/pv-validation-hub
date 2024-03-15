import { fakeHomepageNote, fakeHomepageValidationGist } from './fake_data_service.js';

const HomepageService = {
  getHighlights() {
    return fakeHomepageNote();
  },

  getValidationHubGist() {
    return fakeHomepageValidationGist();
  },
};

export default HomepageService;
