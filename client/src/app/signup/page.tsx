"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { Eye, EyeOff, Mail, User, Lock, Trophy, Check, X, ArrowLeft } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"

interface FormData {
    username: string
    email: string
    password: string
    confirmPassword: string
}

interface FormErrors {
    username?: string
    email?: string
    password?: string
    confirmPassword?: string
}

export default function SignUpPage() {
    const [formData, setFormData] = useState<FormData>({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
    })

    const [errors, setErrors] = useState<FormErrors>({})
    const [showPassword, setShowPassword] = useState(false)
    const [showConfirmPassword, setShowConfirmPassword] = useState(false)
    const [isLoading, setIsLoading] = useState(false)

    const validateField = (name: string, value: string | boolean) => {
        const newErrors = { ...errors }

        switch (name) {
            case "username":
                if (!value || (value as string).length < 4) {
                    newErrors.username = "Username must be at least 4 characters"
                } else {
                    delete newErrors.username
                }
                break
           case "email":
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
                if (!value || !emailRegex.test(value as string)) {
                    newErrors.email = "Please enter a valid email address"
                } else {
                    delete newErrors.email
                }
                break
            case "password":
                const password = value as string
                if (!password || password.length < 8) {
                    newErrors.password = "Password must be at least 8 characters"
                } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
                    newErrors.password = "Password must contain uppercase, lowercase, and number"
                } else {
                    delete newErrors.password
                }
                break
            case "confirmPassword":
                if (value !== formData.password) {
                    newErrors.confirmPassword = "Passwords do not match"
                } else {
                    delete newErrors.confirmPassword
                }
                break
        }

        setErrors(newErrors)
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type, checked } = e.target
        const fieldValue = type === "checkbox" ? checked : value

        setFormData((prev) => ({
            ...prev,
            [name]: fieldValue,
        }))

        validateField(name, fieldValue)
    }

    const getPasswordStrength = (password: string) => {
        let strength = 0
        if (password.length >= 8) strength++
        if (/[a-z]/.test(password)) strength++
        if (/[A-Z]/.test(password)) strength++
        if (/\d/.test(password)) strength++
        if (/[^a-zA-Z\d]/.test(password)) strength++
        return strength
    }

    const getPasswordStrengthText = (strength: number) => {
        switch (strength) {
            case 0:
            case 1:
                return "Weak"
            case 2:
            case 3:
                return "Medium"
            case 4:
            case 5:
                return "Strong"
            default:
                return "Weak"
        }
    }

    const getPasswordStrengthColor = (strength: number) => {
        switch (strength) {
            case 0:
            case 1:
                return "bg-red-500"
            case 2:
            case 3:
                return "bg-yellow-500"
            case 4:
            case 5:
                return "bg-green-500"
            default:
                return "bg-gray-300"
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        // Validate all fields
        Object.keys(formData).forEach((key) => {
            validateField(key, formData[key as keyof FormData])
        })

        if (Object.keys(errors).length === 0) {
            setIsLoading(true)
            // placeholder simulation until backend is ready
            await new Promise((resolve) => setTimeout(resolve, 2000))
            setIsLoading(false)
            // TODO add handling submission later
            console.log("Form submitted:", formData)
        }
    }

    const passwordStrength = getPasswordStrength(formData.password)

    return (
        <div className="min-h-screen bg-gray-50 flex">
            <div className="hidden lg:flex lg:w-1/2 bg-black text-white relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-red-600/20 to-black/80 z-10" />
                <div className="absolute inset-0 z-20 flex flex-col justify-center p-12">
                    <div className="flex items-center gap-3 mb-8">
                        <Trophy className="h-8 w-8 text-red-600" />
                        <span className="text-2xl font-bold">UFC Predictor</span>
                    </div>
                    <h1 className="text-4xl font-bold mb-4">Join the Ultimate Fighting Community</h1>
                    <p className="text-xl text-gray-300 mb-8">
                        Get access to a community of hardcore MMA fans and advanced AI Predictions.
                    </p>
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                                <Check className="w-4 h-4" />
                            </div>
                            <span>Expert fight predictions with 75% accuracy</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                                <Check className="w-4 h-4" />
                            </div>
                            <span>Detailed fighter statistics and analysis</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                                <Check className="w-4 h-4" />
                            </div>
                            <span>Free to use prediction model</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="w-full lg:w-1/2 flex items-center justify-center p-6">
                <div className="w-full max-w-md">
                    <div className="lg:hidden flex items-center gap-3 mb-8">
                        <Trophy className="h-6 w-6 text-red-600" />
                        <span className="text-xl font-bold">UFC Predictor</span>
                    </div>

                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6 transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to home
                    </Link>

                    <Card className="border-0 shadow-lg">
                        <CardHeader className="space-y-1 pb-2">
                            <CardTitle className="text-2xl font-bold">Create your account</CardTitle>
                            <CardDescription>Join other MMA fans and get started with your predictions today</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="">
                                <Button variant="outline" className="w-full cursor-pointer" type="button">
                                    <User/>
                                    Continue as a Guest
                                </Button>
                            </div>

                            <div className="relative">
                                <div className="absolute inset-0 flex items-center">
                                    <Separator />
                                </div>
                                <div className="relative flex justify-center text-xs uppercase">
                                    <span className="bg-white px-2 text-muted-foreground">Or continue with email</span>
                                </div>
                            </div>

                            <form onSubmit={handleSubmit} className="space-y-4">
                                {/*Name fields*/}
                                <div className="space-y-2">
                                    <Label htmlFor="username">Username</Label>
                                    <div className="relative">
                                        <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input
                                            id="username"
                                            name="username"
                                            type="username"
                                            placeholder="johndoe3"
                                            value={formData.username}
                                            onChange={handleInputChange}
                                            className={`pl-10 ${errors.username ? "border-red-500" : ""}`}
                                        />
                                        {errors.username ? (
                                            <X className="absolute right-3 top-3 h-4 w-4 text-red-500" />
                                        ) : formData.username && !errors.username ? (
                                            <Check className="absolute right-3 top-3 h-4 w-4 text-green-500" />
                                        ) : null}
                                    </div>
                                    {errors.username && <p className="text-xs text-red-500">{errors.username}</p>}
                                </div>

                                {/* Email field */}
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email address</Label>
                                    <div className="relative">
                                        <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input
                                            id="email"
                                            name="email"
                                            type="email"
                                            placeholder="john.doe@example.com"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            className={`pl-10 ${errors.email ? "border-red-500" : ""}`}
                                        />
                                        {errors.email ? (
                                            <X className="absolute right-3 top-3 h-4 w-4 text-red-500" />
                                        ) : formData.email && !errors.email ? (
                                            <Check className="absolute right-3 top-3 h-4 w-4 text-green-500" />
                                        ) : null}
                                    </div>
                                    {errors.email && <p className="text-xs text-red-500">{errors.email}</p>}
                                </div>

                                {/* Password field */}
                                <div className="space-y-2">
                                    <Label htmlFor="password">Password</Label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input
                                            id="password"
                                            name="password"
                                            type={showPassword ? "text" : "password"}
                                            placeholder="Create a strong password"
                                            value={formData.password}
                                            onChange={handleInputChange}
                                            className={`pl-10 pr-10 ${errors.password ? "border-red-500" : ""}`}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                                        >
                                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                        </button>
                                    </div>
                                    {formData.password && (
                                        <div className="space-y-2">
                                            <div className="flex items-center justify-between text-xs">
                                                <span>Password strength:</span>
                                                <span
                                                    className={`font-medium ${
                                                        passwordStrength <= 1
                                                            ? "text-red-500"
                                                            : passwordStrength <= 3
                                                                ? "text-yellow-500"
                                                                : "text-green-500"
                                                    }`}
                                                >
                                                    {getPasswordStrengthText(passwordStrength)}
                                                </span>
                                            </div>
                                            <div className="flex gap-1">
                                                {[1, 2, 3, 4, 5].map((level) => (
                                                    <div
                                                        key={level}
                                                        className={`h-1 flex-1 rounded-full ${
                                                            level <= passwordStrength ? getPasswordStrengthColor(passwordStrength) : "bg-gray-200"
                                                        }`}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                    {errors.password && <p className="text-xs text-red-500">{errors.password}</p>}
                                </div>

                                {/* Confirm password field */}
                                <div className="space-y-2">
                                    <Label htmlFor="confirmPassword">Confirm password</Label>
                                    <div className="relative">
                                        <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                        <Input
                                            id="confirmPassword"
                                            name="confirmPassword"
                                            type={showConfirmPassword ? "text" : "password"}
                                            placeholder="Confirm your password"
                                            value={formData.confirmPassword}
                                            onChange={handleInputChange}
                                            className={`pl-10 pr-10 ${errors.confirmPassword ? "border-red-500" : ""}`}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                            className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                                        >
                                            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                        </button>
                                    </div>
                                    {errors.confirmPassword && <p className="text-xs text-red-500">{errors.confirmPassword}</p>}
                                </div>
                                <Button
                                    type="submit"
                                    className="w-full cursor-pointer bg-red-600 hover:bg-red-700"
                                    disabled={isLoading || Object.keys(errors).length > 0}
                                >
                                    {isLoading ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                            Creating account...
                                        </>
                                    ) : (
                                        "Create account"
                                    )}
                                </Button>
                            </form>

                            <div className="text-center text-sm text-gray-600">
                                Already have an account?{" "}
                                <Link href="/signin" className="text-red-600 hover:underline font-medium">
                                    Sign in
                                </Link>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
