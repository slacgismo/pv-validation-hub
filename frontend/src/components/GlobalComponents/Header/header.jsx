import * as React from 'react';
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
import { useNavigate } from "react-router-dom";
import { useState } from 'react';
import Cookies from 'universal-cookie';
import { faker } from "@faker-js/faker";

export default function Header () {
  const cookies = new Cookies();
  const navigate = useNavigate();
  const [anchorElUser, setAnchorElUser] = useState(null);

  const userInfoMenu = [
    {
      "text": "profile",
      "handler": () => {
        navigate("/profile/"+cookies.get("user").id);
      }
    },
    {
      "text": "logout",
      "handler": () => {
        cookies.remove("user", {path: "/"});
        navigate("/");
      }
    }
  ];

  const handleOpenUserMenu = (event) => {
    setAnchorElUser(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorElUser(null);
  };
  
  const handleCloseNavMenu = (location) => {
    if (location === "Dashboard") {
      location = "Submission" + "/1";
    }
    navigate("/" + location);
  };

  const pages = ['Analyses', 'Datasets', 'Dashboard'];

  const checkUserLoggedOut = () => {
    return cookies.get("user") === undefined || cookies.get("user") === null || cookies.get("user") === "";
  };

  return (
    <Box sx={{ display: 'flex '}}>
      <AppBar position="static" sx={{ backgroundColor: "white" }}>
        <Container maxWidth="xl">
          <Toolbar disableGutters>
            <Logo redirect="/" />
            <NavMenu pages={pages} onClose={handleCloseNavMenu} />
            {
              checkUserLoggedOut() ?
              <UserLoggedInMenu onClick={handleCloseNavMenu} /> :
              <UserInfoMenu userInfoMenu={userInfoMenu} anchorElUser={anchorElUser}
                            onClickUserInfoMenu={handleOpenUserMenu}
                            onCloseUserMenu={handleCloseUserMenu} />
            }
          </Toolbar>
        </Container>
      </AppBar>
    </Box>
  );
};

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
          onClick={() => {onClose(page)}}
          sx={{ my: 2, color: '#18A0FB', display: 'block' }}
          textTransform="none"
        >
          <Typography textTransform="none">{page}</Typography>
        </Button>
      ))}
    </Box>
  );
}

function UserLoggedInMenu({ onClick }) {
  return (
    <Box sx={{ flexGrow: 0, '& button': { m: 1, maxWidth: '8em', minWidth: '8em' } }}>
      <Button onClick={() => onClick("login")} variant="outlined">Login</Button>
      <Button onClick={() => onClick("register")} variant="contained">Register</Button>
    </Box>
  );
}

function UserInfoMenu({ userInfoMenu, anchorElUser, onClickUserInfoMenu, onCloseUserMenu }) {
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
            <MenuItem key={item.text} onClick={item.handler}>
              <Typography textAlign="center">{item.text}</Typography>
            </MenuItem>
          ))
        }
      </Menu>
    </Box>
  );
}
