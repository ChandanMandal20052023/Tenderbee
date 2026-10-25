import { NextRequest, NextResponse } from "next/server";

const BACKEND_INTERNAL_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

async function proxyRequest(request: NextRequest, params: Promise<{ path: string[] }>) {
  const resolvedParams = await params;
  let path = resolvedParams.path.join("/");
  // Preserve trailing slash for Django REST Framework endpoints (unless it points to a static file with extension)
  const isFile = /\.[a-zA-Z0-9]+$/.test(path);
  if (!isFile && !path.endsWith("/")) {
    path = `${path}/`;
  }
  const searchParams = request.nextUrl.search;
  const targetUrl = `${BACKEND_INTERNAL_URL}/${path}${searchParams}`;

  // Forward request headers
  const forwardHeaders = new Headers();
  request.headers.forEach((value, key) => {
    // Avoid forwarding host or connection headers that conflict with node fetch
    if (!["host", "connection"].includes(key.toLowerCase())) {
      forwardHeaders.set(key, value);
    }
  });

  // Pass incoming cookies directly to backend
  const cookieHeader = request.headers.get("cookie");
  if (cookieHeader) {
    forwardHeaders.set("cookie", cookieHeader);
  }

  // Double-submit CSRF token forwarding
  const csrfToken = request.cookies.get("csrftoken")?.value;
  if (csrfToken && !forwardHeaders.has("x-csrftoken")) {
    forwardHeaders.set("x-csrftoken", csrfToken);
  }

  const method = request.method;
  let body: BodyInit | null = null;
  if (!["GET", "HEAD"].includes(method)) {
    const contentType = request.headers.get("content-type") || "";
    if (contentType.includes("multipart/form-data")) {
      const arrayBuffer = await request.arrayBuffer();
      body = Buffer.from(arrayBuffer);
      forwardHeaders.set("content-length", body.length.toString());
    } else {
      body = await request.text();
    }
  }

  try {
    const backendResponse = await fetch(targetUrl, {
      method,
      headers: forwardHeaders,
      body,
      redirect: "manual",
      // @ts-ignore
      cache: "no-store",
    });

    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      // Forward Set-Cookie headers properly
      if (key.toLowerCase() === "set-cookie") {
        responseHeaders.append(key, value);
      } else {
        responseHeaders.set(key, value);
      }
    });

    const responseBody = await backendResponse.arrayBuffer();
    return new NextResponse(responseBody, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch (error: any) {
    console.error(`[Next.js Backend Proxy Error] ${method} ${targetUrl}:`, error);
    return NextResponse.json(
      { error: `Service unavailable. Failed to reach backend core: ${error?.message || error}` },
      { status: 503 }
    );
  }
}

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, params);
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, params);
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, params);
}

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, params);
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxyRequest(request, params);
}
