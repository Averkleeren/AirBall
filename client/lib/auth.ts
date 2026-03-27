export type AuthenticatedUser = {
  id: string;
  email?: string | null;
  username?: string | null;
};

export type AuthSession = {
  access_token: string;
  refresh_token?: string;
  user: AuthenticatedUser;
};

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user";

export function storeAuthSession(session: AuthSession) {
  localStorage.setItem(ACCESS_TOKEN_KEY, session.access_token);

  if (session.refresh_token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, session.refresh_token);
  }

  localStorage.setItem(USER_KEY, JSON.stringify(session.user));
}

export function getAccessToken() {
  return typeof window === "undefined"
    ? null
    : localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function clearAuthSession() {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
