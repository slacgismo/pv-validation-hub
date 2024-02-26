import React, { useContext, useState } from 'react';
import { Edit } from '@mui/icons-material';
import {
  Box,
  Card,
  Stack,
  Typography,
  Avatar,
  Button,
  TextField,
} from '@mui/material';
import Cookies from 'universal-cookie';
import YouTag from './YouTag.jsx';
import CommentContext from './CommentContext.js';

function OwnReply({
  onContent, onCount, onTar, onDel, comId,
}) {
  const cookies = new Cookies();
  const commentUser = cookies.get('user');
  const { IMGOBJ } = useContext(CommentContext);
  const prsAva = IMGOBJ[`${commentUser.username}`];

  const [clicked, setClicked] = useState(false);
  const [editingRep, setEditingRep] = useState(false);
  const [repText, setRepText] = useState(onContent);

  return (
    <Card>
      <Box sx={{ p: '15px' }}>
        <Stack spacing={2} direction="row">
          <Box sx={{ width: '100%' }}>
            <Stack
              spacing={2}
              direction="row"
              justifyContent="space-between"
              alignItems="center"
            >
              <Stack spacing={2} direction="row" alignItems="center">
                <Avatar src={prsAva} />
                <Typography
                  fontWeight="bold"
                  sx={{ color: 'neutral.darkBlue' }}
                >
                  {commentUser.username}
                </Typography>
                <YouTag />
                <Typography sx={{ color: 'neutral.grayishBlue' }}>
                  Just now
                </Typography>
              </Stack>
              <Stack direction="row" spacing={1}>
                <Button
                  variant="text"
                  disabled={clicked}
                  sx={{
                    fontWeight: 500,
                    textTransform: 'capitalize',
                    color: 'custom.moderateBlue',
                  }}
                  startIcon={<Edit />}
                  onClick={() => {
                    setClicked(!clicked);
                    setEditingRep(!editingRep);
                  }}
                >
                  Edit
                </Button>
              </Stack>
            </Stack>
            {editingRep ? (
              <>
                <TextField
                  sx={{ p: '20px 0' }}
                  multiline
                  fullWidth
                  minRows={4}
                  id="outlined-multilined"
                  placeholder="Don't leave this blank!"
                  value={repText}
                  onChange={(e) => {
                    setRepText(e.target.value);
                  }}
                />
                <Button
                  sx={{
                    bgcolor: 'custom.moderateBlue',
                    color: 'neutral.white',
                    p: '8px 25px',
                    float: 'right',
                    '&:hover': {
                      bgcolor: 'custom.lightGrayishBlue',
                    },
                  }}
                  onClick={() => {
                    !repText.trim()
                      ? alert('Read the placeholder.')
                      : setEditingRep(!editingRep);
                    setClicked(!clicked);
                  }}
                >
                  Update
                </Button>
              </>
            ) : (
              <Typography
                component="div"
                sx={{ color: 'neutral.grayishBlue', p: '20px 0' }}
              >
                <Typography
                  sx={{
                    color: 'custom.moderateBlue',
                    width: 'fit-content',
                    display: 'inline-block',
                    fontWeight: 500,
                  }}
                >
                  {`@${onTar}`}
                </Typography>
                {' '}
                {repText}
              </Typography>
            )}
          </Box>
        </Stack>
      </Box>
    </Card>
  );
}

export default OwnReply;
