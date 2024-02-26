import React, { createContext, useState } from 'react';
import Cookies from 'universal-cookie';
import { DashboardService } from '../../../services/dashboard_service.js';

const CommentContext = createContext();

export function CommentProvider({ children }) {
  const cookies = new Cookies();
  const commentUser = cookies.get('user');
  const data = DashboardService.getDiscussionComments('', commentUser.username);
  const [currentUser, comments] = [data.currentUser, data.comments];
  const [commentSection, setCommentSection] = useState(comments);
  const IMGOBJ = DashboardService.getImageObjects();
  const addComment = (data) => {
    setCommentSection([
      ...commentSection,
      {
        id: Math.floor(Math.random() * 10000),
        content: data,
        createdAt: 'Just now',
        score: 0,
        replies: [],
        user: { username: commentUser.username },
      },
    ]);
  };
  return (
    <CommentContext.Provider
      value={{
        currentUser,
        commentSection,
        IMGOBJ,
        addComment,
      }}
    >
      {children}
    </CommentContext.Provider>
  );
}

export default CommentContext;
