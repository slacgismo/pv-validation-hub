import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import Tooltip from '@mui/material/Tooltip';
import MenuItem from '@mui/material/MenuItem';
import { useNavigate } from 'react-router-dom';
import Cookies from 'universal-cookie';
// eslint-disable-next-line
import { faker } from '@faker-js/faker';
import Divider from '@mui/material/Divider';
import PropTypes from 'prop-types';

export default function Header() {
  const cookies = new Cookies();
  const navigate = useNavigate();
  const [anchorElUser, setAnchorElUser] = useState(null);

  const userInfoMenu = [
    {
      text: 'Developer',
      handler: () => {
        navigate('/developer');
      },
      border: true,
    },
    {
      text: 'Profile',
      handler: () => {
        navigate('/profile');
      },
      border: false,
    },
    {
      text: 'Logout',
      handler: () => {
        cookies.remove('user', { path: '/' });
        navigate('/');
      },
      border: false,
    },
  ];

  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };

  const handleCloseNavMenu = (location) => {
    let relocation = location;
    if (relocation === 'Dashboard') {
      relocation = 'Submission/1';
    }
    navigate(`/${relocation}`);
  };

  // disabled pages , 'Datasets', 'Dashboard'
  const pages = ['Analyses'];

  const checkUserLoggedOut = () => cookies.get('user') === undefined || cookies.get('user') === null || cookies.get('user') === '';

  return (
    <Box sx={{ display: 'flex ' }}>
      <AppBar position="fixed" sx={{ backgroundColor: 'white' }}>
        <Container maxWidth="xl">
          <Toolbar disableGutters>
            <Logo redirect="/" />
            <NavMenu pages={pages} onClose={handleCloseNavMenu} />
            {
              checkUserLoggedOut()
                ? <UserLoggedInMenu onClick={handleCloseNavMenu} />
                : (
                  <UserInfoMenu
                    userInfoMenu={userInfoMenu}
                    anchorElUser={anchorElUser}
                    onClickUserInfoMenu={handleOpenUserMenu}
                    onCloseUserMenu={handleCloseUserMenu}
                  />
                )
            }
          </Toolbar>
        </Container>
      </AppBar>
    </Box>
  );
}

function Logo({ redirect }) {
  return (
    <Typography
      variant="h6"
      noWrap
      component="a"
      href={redirect}
      sx={{
        mr: 2,
        display: { xs: 'none', md: 'flex' },
        fontFamily: 'sans-serif',
        fontWeight: 700,
        color: 'black',
        textDecoration: 'none',
      }}
    >
      PVHub
    </Typography>
  );
}

function NavMenu({ pages, onClose }) {
  return (
    <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
      {pages.map((page) => (
        <Button
          key={page}
          onClick={() => { onClose(page); }}
          sx={{ my: 2, color: '#18A0FB', display: 'block' }}
          texttransform="none"
        >
          <Typography texttransform="none">{page}</Typography>
        </Button>
      ))}
    </Box>
  );
}

function UserLoggedInMenu({ onClick }) {
  return (
    <Box sx={{ flexGrow: 0, '& button': { m: 1, maxWidth: '8em', minWidth: '8em' } }}>
      <Button onClick={() => onClick('login')} variant="outlined">
        <Typography texttransform="none">
          Sign In
        </Typography>
      </Button>
      <Button onClick={() => onClick('register')} variant="contained">
        <Typography texttransform="none">
          Register
        </Typography>
      </Button>
    </Box>
  );
}

function UserInfoMenu({
  userInfoMenu, anchorElUser, onClickUserInfoMenu, onCloseUserMenu,
}) {
  return (
    <Box sx={{ flexGrow: 0 }}>
      <Tooltip title="Open settings">
        <IconButton onClick={onClickUserInfoMenu} sx={{ p: 0 }}>
          <Avatar alt="User" src={faker.image.avatar()} />
        </IconButton>
      </Tooltip>

      <Menu
        sx={{ mt: '45px' }}
        id="menu-appbar"
        anchorEl={anchorElUser}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorElUser)}
        onClose={onCloseUserMenu}
      >
        {
          userInfoMenu.map((item) => (
            <Box>
              <MenuItem key={item.text} onClick={item.handler}>
                <Typography textAlign="center">{item.text}</Typography>
              </MenuItem>
              { item.border ? <Divider /> : <Box /> }
            </Box>
          ))
        }
      </Menu>
    </Box>
  );
}

Logo.propTypes = {
  redirect: PropTypes.string.isRequired,
};

NavMenu.propTypes = {
  pages: PropTypes.arrayOf(PropTypes.string).isRequired,
  onClose: PropTypes.func.isRequired,
};

UserLoggedInMenu.propTypes = {
  onClick: PropTypes.func.isRequired,
};

UserInfoMenu.propTypes = {
  userInfoMenu: PropTypes.arrayOf([]).isRequired,
  anchorElUser: PropTypes.oneOfType([
    PropTypes.instanceOf(Node),
    PropTypes.instanceOf(null),
  ]).isRequired,
  onClickUserInfoMenu: PropTypes.func.isRequired,
  onCloseUserMenu: PropTypes.func.isRequired,
};
