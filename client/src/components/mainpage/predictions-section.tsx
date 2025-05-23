import {Badge} from "@/components/ui/badge";
import {Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle} from "@/components/ui/card";
import {CalendarDays, ChevronRight} from "lucide-react";
import {Button} from "@/components/ui/button";

const predictions = [
    {
        date: "Upcoming",
        title: "Islam Makhachev vs Jack Della Maddalena",
        description: "Our advanced model heavily favors Islam Makhachev to win this fight. The model predicts a 78% chance of victory for Makhachev, win method being by way of multi-method: submission/decision with a confidence of 85%. The model also predicts the fight to go into the later rounds, suggesting an OVER 2.5 round bet with a probability of 65%",
        confidence: 4
    },
    {
        date: "June 8th",
        title: "Merab Dvalishvili vs Sean O'Malley",
        description: "Our advanced model heavily favors Merab Dvalishvili to win this fight easily. The model predicts a 83% chance of victory for Dvalishvili, win method being Decision with a confidence of 90%. The model also suggests an OVER 3.5 round bet.",
        confidence: 4
    }
]

export default function PredictionsSection() {
    return (
        <section className="w-full py-12 md:py-24 lg:py-32 flex justify-center">
            <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center justify-center space-y-4 text-center">
                    <div className="space-y-2">
                        <Badge variant="outline" className="border-red-600 text-red-600">
                            Free Predictions
                        </Badge>
                        <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Free Predictions</h2>
                        <p className="max-w-[700px] text-muted-foreground md:text-xl">
                            Check out predictions from our advanced model. Sign up to unlock predictions for any fights.
                        </p>
                    </div>
                </div>

                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 mt-8">
                    {predictions.map((prediction, index) => {
                        return (
                            <div key={index}>
                                <PredictionCard date={prediction.date} title={prediction.title} description={prediction.description} confidence={prediction.confidence} />
                            </div>
                        )
                    })}
                </div>

                <div className="flex justify-center mt-12">
                    <Button size="lg" className="bg-red-600 hover:bg-red-700">
                        Unlock All Predictions
                        <ChevronRight className="ml-2 h-4 w-4" />
                    </Button>
                </div>
            </div>
        </section>
    )
}

interface PredictionCardProps {
    date: string;
    title: string;
    description: string;
    confidence: number;
}

export function PredictionCard(prediction: PredictionCardProps) {
    return (
        <Card className="overflow-hidden h-[47vh]">
            <CardHeader className="p-0 h-1">
                <div className="flex justify-between items-center px-3">
                    <Badge className="bg-red-600 hover:bg-red-700">FREE PREDICTION</Badge>
                    <div className="flex items-center text-xs text-muted-foreground">
                        <CalendarDays className="mr-1 h-3 w-3" />
                        {prediction.date}
                    </div>
                </div>
            </CardHeader>
            <CardContent className="p-4">
                <CardTitle className="text-xl mb-2">{prediction.title}</CardTitle>
                <CardDescription>
                    {prediction.description}
                </CardDescription>
            </CardContent>
            <CardFooter className="p-4 pt-0 flex justify-between">
                <div className="flex items-center text-sm">
                    <span className="font-medium">Confidence:</span>
                    <div className="ml-2 flex">
                        {Array.from(Array(prediction.confidence).keys()).map((i) => (
                            <div key={i} className="w-2 h-4 bg-red-600 mr-0.5 rounded-sm"></div>
                        ))}
                        {Array.from(Array(5 - prediction.confidence).keys()).map((i) => (
                            <div key={i} className="w-2 h-4 bg-gray-200 mr-0.5 rounded-sm"></div>
                        ))}
                    </div>
                </div>
            </CardFooter>
        </Card>
    )
}
