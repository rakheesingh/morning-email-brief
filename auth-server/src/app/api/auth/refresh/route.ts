import { NextRequest, NextResponse } from "next/server";
import { google } from "googleapis";

export async function POST(request: NextRequest) {
  try {
    const { refresh_token } = await request.json();

    if (!refresh_token) {
      return NextResponse.json({ error: "Missing refresh_token" }, { status: 400 });
    }

    const clientId = process.env.GMAIL_CLIENT_ID!;
    const clientSecret = process.env.GMAIL_CLIENT_SECRET!;

    const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret);
    oAuth2Client.setCredentials({ refresh_token });

    const { credentials } = await oAuth2Client.refreshAccessToken();

    return NextResponse.json({
      access_token: credentials.access_token,
      expiry_date: credentials.expiry_date,
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message || "Token refresh failed" },
      { status: 500 }
    );
  }
}
