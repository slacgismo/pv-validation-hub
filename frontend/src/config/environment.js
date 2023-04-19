const ENVIRONMENT_DEVELOPMENT = 'DEVELOPMENT';
const ENVIRONMENT_STAGING = 'STAGING';
const ENVIRONMENT_PRODUCTION = 'PRODUCTION';

const BASE_API_URL_APP_DEVELOPMENT = 'http://localhost:8005';
const BASE_API_URL_APP_STAGING = 'https://TODO.org';
const BASE_API_URL_APP_PRODUCTION = 'https://api.pv-validation-hub.org';

const parseEnvironment = () => {
  if (window.location.hostname.includes('localhost')) return ENVIRONMENT_DEVELOPMENT;
  if (window.location.hostname.includes('staging')) return ENVIRONMENT_STAGING;
  return ENVIRONMENT_PRODUCTION;
};

export const ENVIRONMENT = parseEnvironment();
export const isDevelopment = () => (ENVIRONMENT === ENVIRONMENT_DEVELOPMENT);
export const isStaging = () => (ENVIRONMENT === ENVIRONMENT_STAGING);
export const isProduction = () => (ENVIRONMENT === ENVIRONMENT_PRODUCTION);

let baseApiUrlApp;
if (isDevelopment()) baseApiUrlApp = BASE_API_URL_APP_DEVELOPMENT;
else if (isStaging()) baseApiUrlApp = BASE_API_URL_APP_STAGING;
else if (isProduction()) baseApiUrlApp = BASE_API_URL_APP_PRODUCTION;

let hubapi = {
  api: {
    defaultTimeout: 60000,
    baseUrl: {
      app: baseApiUrlApp,
    },
  },
};

export default hubapi; 