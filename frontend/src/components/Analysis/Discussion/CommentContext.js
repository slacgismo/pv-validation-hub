import React, { createContext, useState } from 'react';
import Cookies from 'universal-cookie';
import PropTypes from 'prop-types';
import DashboardService from '../../../services/dashboard_service.js';

const CommentContext = createContext();

export function CommentProvider({ children }) {
  const cookies = new Cookies();
  const commentUser = cookies.get('user');
  const data = DashboardService.getDiscussionComments('', commentUser.username);
  const [currentUser, comments] = [data.currentUser, data.comments];
  const [commentSection, setCommentSection] = useState(comments);
  const IMGOBJ = DashboardService.getImageObjects();
  const contextValue = React.useMemo(() => {
    const addComment = (commentData) => {
      setCommentSection([
        ...commentSection,
        {
          id: Math.floor(Math.random() * 10000),
          content: commentData,
          createdAt: 'Just now',
          score: 0,
          replies: [],
          user: { username: commentUser.username },
        },
      ]);
    };

    return {
      currentUser,
      commentSection,
      IMGOBJ,
      addComment,
    };
  }, [currentUser, commentSection, IMGOBJ, commentUser.username]);

  return (
    <CommentContext.Provider value={contextValue}>
      {children}
    </CommentContext.Provider>
  );
}

CommentProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default CommentContext;
