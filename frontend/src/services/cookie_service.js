import Cookies from 'universal-cookie';

const CookieService = {
  getUserCookie() {
    const cookies = new Cookies();
    return cookies.get('user');
  },
};

export default CookieService;
