import { apiRequest } from "./http";
import type { User } from "../types/user";
import type { PrivacySettings } from "../types/settings";

export const authApi = {
  login: (email: string, password: string) =>
    apiRequest<{ access: string; refresh: string }>("/auth/token_bad", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (data: Record<string, string>) =>
    apiRequest<User>("/accounts/register/", { method: "POST", body: JSON.stringify(data) }),
  me: () => apiRequest<User>("/accounts/me/"),
  updateMe: (data: Partial<User>) =>
    apiRequest<User>("/accounts/me/", { method: "PATCH", body: JSON.stringify(data) }),
  verifyEmail: (token: string) =>
    apiRequest("/accounts/verify-email/" + token + "/", { method: "POST" }),
  forgotPassword: (email: string) =>
    apiRequest("/accounts/forgot-password/", { method: "POST", body: JSON.stringify({ email }) }),
  resetPassword: (token: string, password: string) =>
    apiRequest("/accounts/reset-password/" + token + "/", {
      method: "POST",
      body: JSON.stringify({ password }),
    }),
  getPrivacy: () => apiRequest<PrivacySettings>("/accounts/privacy/"),
  updatePrivacy: (data: Partial<PrivacySettings>) =>
    apiRequest<PrivacySettings>("/accounts/privacy/", { method: "PATCH", body: JSON.stringify(data) }),
  getIdentity: () => apiRequest<Record<string, unknown>>("/accounts/identity/"),
  updateIdentity: (data: FormData) =>
    apiRequest("/accounts/identity/", { method: "PATCH", body: data }),
}
