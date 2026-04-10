import { NextRequest, NextResponse } from "next/server";
import { google } from "googleapis";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const error = request.nextUrl.searchParams.get("error");

  if (error) {
    return NextResponse.redirect(new URL(`/auth/error?message=${error}`, request.url));
  }

  if (!code) {
    return NextResponse.redirect(new URL("/auth/error?message=missing_code", request.url));
  }

  const clientId = process.env.GMAIL_CLIENT_ID!;
  const clientSecret = process.env.GMAIL_CLIENT_SECRET!;
  const redirectUri = process.env.GOOGLE_REDIRECT_URI || `${process.env.NEXT_PUBLIC_BASE_URL}/api/auth/callback`;

  const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

  try {
    const { tokens } = await oAuth2Client.getToken(code);

    const tokenData = {
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
      expiry_date: tokens.expiry_date,
      scope: tokens.scope,
      token_type: tokens.token_type,
    };

    const encodedTokens = Buffer.from(JSON.stringify(tokenData)).toString("base64url");

    const cliRedirect = `http://localhost:9587/callback?tokens=${encodedTokens}`;
    return NextResponse.redirect(cliRedirect);
  } catch (err: any) {
    const message = encodeURIComponent(err.message || "token_exchange_failed");
    return NextResponse.redirect(new URL(`/auth/error?message=${message}`, request.url));
  }
}
