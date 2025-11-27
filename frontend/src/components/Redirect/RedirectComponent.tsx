import React from 'react';
import { Navigate, useParams } from 'react-router-dom';

interface RedirectComponentProps {
  to: string;
  replace?: boolean;
}

const RedirectComponent: React.FC<RedirectComponentProps> = ({ to, replace = true }) => {
  const params = useParams();
  
  // Replace parameters in the destination URL
  let destination = to;
  Object.entries(params).forEach(([key, value]) => {
    destination = destination.replace(`:${key}`, value || '');
  });
  
  return <Navigate to={destination} replace={replace} />;
};

export default RedirectComponent;
